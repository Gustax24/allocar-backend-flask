from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Referral(db.Model, UUIDMixin):
    __tablename__ = "referrals"

    referrer_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    referee_id  = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    code_used   = db.Column(db.String(40), nullable=False)
    bonus_referrer = db.Column(db.Numeric(12,2), nullable=False, default=0)
    bonus_referee  = db.Column(db.Numeric(12,2), nullable=False, default=0)
    status = db.Column(db.String(16), nullable=False, default="granted")  # granted|revoked
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
