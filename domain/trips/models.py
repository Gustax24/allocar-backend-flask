from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Trip(db.Model, UUIDMixin):
    __tablename__ = "trips"

    driver_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    origin_lat = db.Column(db.Float, nullable=False)
    origin_lon = db.Column(db.Float, nullable=False)
    origin_text = db.Column(db.String(255), nullable=False)

    destination_lat = db.Column(db.Float, nullable=False)
    destination_lon = db.Column(db.Float, nullable=False)
    destination_text = db.Column(db.String(255), nullable=False)

    departure_time = db.Column(db.DateTime(timezone=True), nullable=False)
    arrival_eta = db.Column(db.DateTime(timezone=True), nullable=True)

    price_per_seat = db.Column(db.Numeric(12,2), nullable=False)
    seats_available = db.Column(db.Integer, nullable=False, default=1)
    luggage_policy = db.Column(db.String(255), nullable=True)
    rules = db.Column(db.String(255), nullable=True)
    allow_auto_accept = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(32), nullable=False, default="published")  # draft|published|ongoing|completed|cancelled

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class TripStop(db.Model, UUIDMixin):
    __tablename__ = "trip_stops"

    trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    order = db.Column(db.Integer, nullable=False, default=0)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    label = db.Column(db.String(255), nullable=False)
    pickup_allowed = db.Column(db.Boolean, default=True)
    dropoff_allowed = db.Column(db.Boolean, default=True)
