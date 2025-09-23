import secrets
from common.errors import APIError
from extensions.db import db
from domain.trips.repository import get as get_trip
from .repository import get, create, add_event, save, list_by_passenger, list_by_driver
from domain.audit.services import audit as audit_log

def create_booking(passenger_id, trip_id, seats):
    trip = get_trip(trip_id)
    if not trip or trip.status not in ("published", "ongoing"):
        raise APIError("not_found", "Trajet non disponible", 404)
    if seats < 1 or seats > int(trip.seats_available):
        raise APIError("booking_conflict", "Nombre de sièges indisponible", 409)
    b = create(trip, passenger_id, seats)
    add_event(b.id, None, "pending", "user", {"seats": seats})
    # auto-accept si le driver a activé ce mode
    if trip.allow_auto_accept:
        return accept_booking(trip.driver_id, b.id)


    return b

def ensure_driver_owns(booking_id, driver_id):
    b = get(booking_id)
    if not b:
        raise APIError("not_found", "Réservation introuvable", 404)
    from domain.trips.models import Trip
    trip = db.session.get(Trip, b.trip_id)
    if not trip or str(trip.driver_id) != str(driver_id):
        raise APIError("forbidden", "Accès refusé", 403)
    return b, trip

def accept_booking(driver_id, booking_id):
    b, trip = ensure_driver_owns(booking_id, driver_id)
    if b.status != "pending":
        raise APIError("conflict", "Réservation non en attente", 409)
    if b.seats > trip.seats_available:
        raise APIError("booking_conflict", "Pas assez de sièges", 409)
    b.status = "accepted"
    save(b); add_event(b.id, "pending", "accepted", "driver")

    audit_log("user", driver_id, "booking.accept", "booking", b.id)
    return b

def reject_booking(driver_id, booking_id):
    b, _ = ensure_driver_owns(booking_id, driver_id)
    if b.status != "pending":
        raise APIError("conflict", "Réservation non en attente", 409)
    b.status = "cancelled"
    save(b); add_event(b.id, "pending", "cancelled", "driver", {"reason":"rejected"})
    audit_log("user", driver_id, "booking.reject", "booking", b.id)
    return b

def cancel_booking(user_id, booking_id):
    b = get(booking_id)
    if not b: raise APIError("not_found", "Réservation introuvable", 404)
    if b.passenger_id != user_id:
        # passager uniquement dans ce MVP
        raise APIError("forbidden", "Seul le passager peut annuler ici", 403)
    if b.status in ("completed", "cancelled"):
        raise APIError("conflict", "Réservation non annulable", 409)
    prev = b.status
    b.status = "cancelled"
    save(b); add_event(b.id, prev, "cancelled", "user")
    audit_log("user", user_id, "booking.cancel", "booking", b.id)
    return b

def checkin_booking(driver_id, booking_id):
    b, _ = ensure_driver_owns(booking_id, driver_id)
    if b.status not in ("accepted", "paid"):
        raise APIError("conflict", "Check-in impossible", 409)
    if not b.qr_code:
        b.qr_code = secrets.token_hex(8)
    save(b); add_event(b.id, b.status, b.status, "driver", {"checkin":"ok"})
    return b

def start_ride(driver_id, booking_id):
    b, _ = ensure_driver_owns(booking_id, driver_id)
    if b.status not in ("accepted", "paid"):
        raise APIError("conflict", "Trajet non démarrable", 409)
    add_event(b.id, b.status, b.status, "driver", {"start":"ok"})
    audit_log("user", driver_id, "booking.start_ride", "booking", b.id)
    return b

def end_ride(driver_id, booking_id):
    b, trip = ensure_driver_owns(booking_id, driver_id)
    if b.status not in ("paid", "accepted"):
        raise APIError("conflict", "Trajet non clôturable", 409)
    prev = b.status
    b.status = "completed"
    save(b); add_event(b.id, prev, "completed", "driver")
    audit_log("user", driver_id, "booking.end_ride", "booking", b.id)
    return b

def after_payment_set_paid(booking_id):
    b = get(booking_id)
    if not b:
        raise APIError("not_found", "Réservation introuvable", 404)
    if b.status in ("cancelled", "completed"):
        return b
    # Décrément atomique et sûr contre la concurrence
    rows = db.session.execute(
        db.text("""
            UPDATE trips
               SET seats_available = seats_available - :s
             WHERE id = :tid
               AND seats_available >= :s
            RETURNING id
        """),
        {"tid": str(b.trip_id), "s": int(b.seats)}
    ).rowcount

    if rows == 0:
        db.session.rollback()
        raise APIError("booking_conflict", "Plus assez de sièges au paiement", 409)

    if b.status != "paid":
        prev = b.status
        b.status = "paid"
        add_event(b.id, prev, "paid", "system")
    db.session.commit()
    return b


def list_bookings_by_role(user_id, role, status=None):
    if role == "passenger":
        return list_by_passenger(user_id, status)
    else:
        return list_by_driver(user_id, status)
