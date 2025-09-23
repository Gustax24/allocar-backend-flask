from extensions.db import db
from .models import Booking, BookingEvent
from domain.trips.models import Trip
from sqlalchemy.orm import joinedload

def get(booking_id):
    return db.session.get(Booking, booking_id)

def create(trip: Trip, passenger_id, seats: int):
    amount = float(trip.price_per_seat) * seats
    b = Booking(trip_id=trip.id, passenger_id=passenger_id, seats=seats, amount_total=amount, status="pending")
    db.session.add(b)
    db.session.commit()
    return b

def add_event(booking_id, from_s, to_s, by, meta=None):
    e = BookingEvent(booking_id=booking_id, from_status=from_s, to_status=to_s, by=by, meta=meta or {})
    db.session.add(e)
    db.session.commit()
    return e

def save(entity):
    db.session.commit()
    return entity

def list_by_passenger(user_id, status=None):
    q = db.session.query(Booking).filter(Booking.passenger_id == user_id)
    if status: q = q.filter(Booking.status == status)
    return q.order_by(Booking.created_at.desc()).all()

def list_by_driver(user_id, status=None):
    # join with trips to filter by driver
    q = db.session.query(Booking).join(Trip, Trip.id == Booking.trip_id).filter(Trip.driver_id == user_id)
    if status: q = q.filter(Booking.status == status)
    return q.order_by(Booking.created_at.desc()).all()
