from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from extensions.db import db
from domain.payments.models import Payment
from domain.bookings.models import Booking
from domain.trips.models import Trip
from domain.users.models import User
from sqlalchemy import func, text

def _window(qs, date_from, date_to, col):
    if date_from:
        qs = qs.filter(col >= datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc))
    if date_to:
        qs = qs.filter(col <= datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc))
    return qs

def finance_report(date_from=None, date_to=None):
    # total paiements paid
    q = db.session.query(func.sum(Payment.amount)).filter(Payment.status == "paid")
    q = _window(q, date_from, date_to, Payment.created_at)
    total_payments = float(q.scalar() or 0)

    # bookings completed
    qb = db.session.query(func.count(Booking.id)).filter(Booking.status == "completed")
    qb = _window(qb, date_from, date_to, Booking.created_at)
    total_completed = int(qb.scalar() or 0)

    revenue_estimate = total_payments * 0.10  # hypothèse 10% commission
    return {
        "total_payments": total_payments,
        "total_completed_bookings": total_completed,
        "revenue_estimate": revenue_estimate
    }

def usage_report(date_from=None, date_to=None):
    # trips published
    qt = db.session.query(func.count(Trip.id)).filter(Trip.status == "published")
    qt = _window(qt, date_from, date_to, Trip.created_at)
    trips_published = int(qt.scalar() or 0)

    # bookings created
    qb = db.session.query(func.count(Booking.id))
    qb = _window(qb, date_from, date_to, Booking.created_at)
    bookings_created = int(qb.scalar() or 0)

    # active users (driver ou passenger) – maintenant compatible SA 2.x + filtre période
    base_sql = """
        SELECT COUNT(DISTINCT u_id) AS c
        FROM (
          SELECT driver_id   AS u_id, created_at FROM trips
          UNION ALL
          SELECT passenger_id AS u_id, created_at FROM bookings
        ) t
        WHERE 1=1
    """
    params = {}
    if date_from:
        start_dt = datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
        base_sql += " AND t.created_at >= :start_dt"
        params["start_dt"] = start_dt
    if date_to:
        end_dt = datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc)
        base_sql += " AND t.created_at <= :end_dt"
        params["end_dt"] = end_dt

    active_users = int(db.session.execute(text(base_sql), params).scalar() or 0)

    return {
        "trips_published": trips_published,
        "bookings_created": bookings_created,
        "active_users": active_users
    }
