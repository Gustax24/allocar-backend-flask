from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Message(db.Model, UUIDMixin):
    __tablename__ = "messages"

    booking_id = db.Column(db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    from_user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.String(16), nullable=False, default="text")  # text|image
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
