from flask_smorest import Blueprint
from flask import request
from domain.payments.services import handle_webhook

# Pour une vraie intégration : valider la signature Stripe via Stripe-Signature.
# Ici, on suppose que la validation est faite côté gateway ou via env.

blp = Blueprint("stripe_webhook", __name__, description="Stripe webhook")

@blp.route("/payments/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_json() or {}
    event_type = payload.get("type")
    data = payload.get("data", {}).get("object", {})
    if event_type == "payment_intent.succeeded":
        p = handle_webhook("stripe", data.get("id"), "paid", None)
        return {"id": str(p.id), "status": p.status}
    elif event_type == "payment_intent.payment_failed":
        p = handle_webhook("stripe", data.get("id"), "failed", None)
        return {"id": str(p.id), "status": p.status}
    return {"ok": True}
