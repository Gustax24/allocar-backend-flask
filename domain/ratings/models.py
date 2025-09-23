from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Rating(db.Model, UUIDMixin):
    __tablename__ = "ratings"

    from_user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    to_user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = db.Column(db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    stars = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
