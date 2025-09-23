from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Dispute(db.Model, UUIDMixin):
    __tablename__ = "disputes"

    booking_id = db.Column(db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    opened_by  = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category   = db.Column(db.String(64), nullable=False)      # paiement, comportement, retard, sécurité...
    description = db.Column(db.String(1024), nullable=False)
    status     = db.Column(db.String(16), nullable=False, default="open")  # open|in_review|resolved|rejected
    resolution = db.Column(db.String(1024), nullable=True)
    resolved_by = db.Column(db.ForeignKey("users.id"), nullable=True)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at  = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
