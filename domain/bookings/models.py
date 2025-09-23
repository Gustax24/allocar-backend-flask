from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Booking(db.Model, UUIDMixin):
    __tablename__ = "bookings"

    trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    passenger_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    seats = db.Column(db.Integer, nullable=False, default=1)
    amount_total = db.Column(db.Numeric(12,2), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")  # pending|accepted|paid|cancelled|completed
    qr_code = db.Column(db.String(64), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class BookingEvent(db.Model, UUIDMixin):
    __tablename__ = "booking_events"

    booking_id = db.Column(db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = db.Column(db.String(32), nullable=True)
    to_status = db.Column(db.String(32), nullable=False)
    by = db.Column(db.String(32), nullable=False)  # user|driver|admin|system
    meta = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
