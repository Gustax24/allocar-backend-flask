from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Promo(db.Model, UUIDMixin):
    __tablename__ = "promos"

    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    type = db.Column(db.String(16), nullable=False, default="amount")  # amount|percent
    value = db.Column(db.Numeric(12,2), nullable=False, default=0)
    max_uses = db.Column(db.Integer, nullable=False, default=0)
    per_user_limit = db.Column(db.Integer, nullable=False, default=1)
    starts_at = db.Column(db.DateTime(timezone=True), nullable=True)
    ends_at = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(db.String(16), nullable=False, default="active")  # active|disabled

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class PromoUsage(db.Model, UUIDMixin):
    __tablename__ = "promo_usages"

    promo_id = db.Column(db.ForeignKey("promos.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id  = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = db.Column(db.ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
