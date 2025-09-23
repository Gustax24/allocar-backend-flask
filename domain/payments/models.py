from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Payment(db.Model, UUIDMixin):
    __tablename__ = "payments"

    booking_id = db.Column(db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    method = db.Column(db.String(32), nullable=False)  # wave|orange|mtn|card|wallet
    provider_ref = db.Column(db.String(128), nullable=True, index=True, unique=True)
    amount = db.Column(db.Numeric(12,2), nullable=False)
    currency = db.Column(db.String(8), nullable=False, default="XOF")
    fees = db.Column(db.Numeric(12,2), nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, default="init")  # init|authorized|paid|failed|refunded
    raw_payload = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
