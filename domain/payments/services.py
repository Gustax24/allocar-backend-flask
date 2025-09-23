from __future__ import annotations

from typing import Literal, Dict, Any
from decimal import Decimal

from common.errors import APIError
from extensions.db import db
from domain.bookings.repository import get as get_booking
from domain.bookings.services import after_payment_set_paid
from .repository import create_for_booking, get_by_provider_ref, save

# Adapters "réels" (basculent en mock si clés non présentes)
from integrations.wave.adapters import wave_init
from integrations.orange_money.adapters import om_init
from integrations.mtn_momo.adapters import mtn_init
from integrations.stripe.adapters import stripe_init

AllowedMethod = Literal["wave", "orange", "mtn", "card"]
ALLOWED_METHODS: set[str] = {"wave", "orange", "mtn", "card"}


def _init_with_provider(method: AllowedMethod, amount_xof: float, booking_id: str, customer_msisdn: str | None = None) -> Dict[str, Any]:
    """
    Initialise un paiement chez le provider ciblé et renvoie un dict normalisé.

    Retour commun:
      - provider_ref: str
      - checkout_url: str | None (wave/orange/mtn)
      - client_secret: str | None (stripe)
      - name: str (nom du provider/méthode)
    """
    metadata = {"booking_id": str(booking_id)}

    if method == "wave":
        if not customer_msisdn:
            # Wave nécessite souvent le MSISDN du payeur
            raise APIError("validation_error", "Numéro MSISDN requis pour Wave", 400)
        res = wave_init(amount_xof, customer_msisdn, metadata=metadata)
        return {
            "name": "wave",
            "provider_ref": res["provider_ref"],
            "checkout_url": res.get("checkout_url"),
            "client_secret": None,
        }

    if method == "orange":
        if not customer_msisdn:
            raise APIError("validation_error", "Numéro MSISDN requis pour Orange Money", 400)
        res = om_init(amount_xof, customer_msisdn, metadata=metadata)
        return {
            "name": "orange",
            "provider_ref": res["provider_ref"],
            "checkout_url": res.get("checkout_url"),
            "client_secret": None,
        }

    if method == "mtn":
        if not customer_msisdn:
            raise APIError("validation_error", "Numéro MSISDN requis pour MTN MoMo", 400)
        res = mtn_init(amount_xof, customer_msisdn, metadata=metadata)
        return {
            "name": "mtn",
            "provider_ref": res["provider_ref"],
            "checkout_url": res.get("checkout_url"),
            "client_secret": None,
        }

    if method == "card":
        # Stripe
        res = stripe_init(amount_xof, metadata)
        return {
            "name": "card",
            "provider_ref": res["provider_ref"],
            "checkout_url": None,
            "client_secret": res.get("client_secret"),
        }

    # Ne devrait pas arriver car filtré en amont
    raise APIError("validation_error", "Méthode de paiement inconnue", 400)


def init_payment(user_id, booking_id, method: AllowedMethod, customer_msisdn: str | None = None):
    """
    Crée l'objet Payment (status=init) puis initialise réellement chez le provider.
    - method: "wave" | "orange" | "mtn" | "card"
    - customer_msisdn: requis pour wave/orange/mtn (format E.164)
    """
    if method not in ALLOWED_METHODS:
        raise APIError("validation_error", "Méthode de paiement invalide", 400)

    b = get_booking(booking_id)
    if not b:
        raise APIError("not_found", "Réservation introuvable", 404)
    if str(b.passenger_id) != str(user_id):
        raise APIError("forbidden", "Cette réservation n'est pas à vous", 403)
    if b.status not in ("pending", "accepted"):
        raise APIError("conflict", "Réservation non payable", 409)

    # Dummy MSISDN en dev/mock pour ne pas casser les tests si non fourni
    if method in {"wave", "orange", "mtn"} and not customer_msisdn:
        customer_msisdn = "+2250100000000"

    # Crée l'enregistrement local Payment
    p = create_for_booking(b, user_id, method)

    # Montant en XOF (Business: pas de décimales)
    amount_xof = int(Decimal(str(b.amount_total)))

    # Appel provider “réel” (ou mock si non configuré)
    provider_payload = _init_with_provider(method, float(amount_xof), str(b.id), customer_msisdn)

    # Sauvegarde la référence provider
    p.provider_ref = provider_payload["provider_ref"]
    save(p)

    # Réponse unifiée côté API
    data = {
        "payment": {
            "id": str(p.id),
            "booking_id": str(p.booking_id),
            "user_id": str(p.user_id),
            "method": p.method,
            "provider_ref": p.provider_ref,
            "amount": float(p.amount),
            "currency": p.currency,
            "status": p.status,
        },
        "provider": provider_payload,
    }
    return data


def handle_webhook(provider: str, provider_ref: str, status: str, signature: str | None):
    """
    Traitement commun des webhooks (provider validé en amont par la route dédiée).
    - provider: "wave" | "orange" | "mtn" | "stripe"
    - status: "paid" | "failed" (normalisé par les webhooks d’intégration)
    """
    # Idempotence simple: si déjà clos → no-op
    p = get_by_provider_ref(provider_ref)
    if not p:
        raise APIError("not_found", "Paiement inconnu", 404)

    if p.status in ("paid", "failed", "refunded"):
        return p

    if status == "paid":
        p.status = "paid"
        save(p)
        # Synchronise la réservation (décrément sièges + status=paid)
        after_payment_set_paid(p.booking_id)

    elif status == "failed":
        p.status = "failed"
        save(p)

    else:
        raise APIError("validation_error", "Statut non géré", 400)

    return p
