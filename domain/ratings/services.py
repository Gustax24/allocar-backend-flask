from common.errors import APIError
from extensions.db import db
from domain.bookings.repository import get as get_booking
from .repository import create, list_for_user, recompute_user_rating

def add_rating(from_user_id, booking_id, to_user_id, stars, comment=None):
    b = get_booking(booking_id)
    if not b or b.status != "completed":
        raise APIError("conflict", "Vous ne pouvez noter qu'après la fin du trajet", 409)
    # doit être membre de la réservation
    from domain.trips.models import Trip
    trip = db.session.get(Trip, b.trip_id)
    if str(from_user_id) not in (str(b.passenger_id), str(trip.driver_id)):
        raise APIError("forbidden", "Pas autorisé", 403)
    r = create(from_user_id=from_user_id, to_user_id=to_user_id, booking_id=booking_id, stars=stars, comment=comment)
    recompute_user_rating(to_user_id)
    return r

def list_user_ratings(user_id, limit=100):
    return list_for_user(user_id, limit)
