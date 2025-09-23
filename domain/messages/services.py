from common.errors import APIError
from extensions.db import db
from extensions.socketio import socketio
from domain.bookings.repository import get as get_booking
from .repository import list_for_booking, create

def ensure_member(booking_id, user_id):
    b = get_booking(booking_id)
    if not b:
        raise APIError("not_found", "Réservation introuvable", 404)
    # membre = passager ou conducteur du trip
    from domain.trips.models import Trip
    trip = db.session.get(Trip, b.trip_id)
    if str(b.passenger_id) != str(user_id) and str(trip.driver_id) != str(user_id):
        raise APIError("forbidden", "Accès refusé au chat", 403)
    return b, trip

def list_messages(user_id, booking_id, limit=50, before=None):
    ensure_member(booking_id, user_id)
    return list_for_booking(booking_id, limit, before)

def post_message(user_id, booking_id, tp, content):
    ensure_member(booking_id, user_id)
    m = create(booking_id, user_id, tp, content)
    # Hook Socket.IO (room par booking)
    socketio.emit("message:new", {
        "id": str(m.id), "booking_id": str(m.booking_id), "from_user_id": str(m.from_user_id),
        "type": m.type, "content": m.content, "created_at": m.created_at.isoformat()
    }, to=f"booking:{m.booking_id}")
    return m
