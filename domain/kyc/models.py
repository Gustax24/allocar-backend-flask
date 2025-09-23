from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class KYCDocument(db.Model, UUIDMixin):
    __tablename__ = "kyc_documents"

    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doc_type = db.Column(db.String(32), nullable=False)  # cni|passport|permis
    doc_number = db.Column(db.String(64), nullable=False)
    front_url = db.Column(db.String(512), nullable=False)
    back_url = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(16), nullable=False, default="pending")  # pending|approved|rejected
    notes = db.Column(db.String(512), nullable=True)
    reviewed_by = db.Column(db.ForeignKey("users.id"), nullable=True)  # admin user id (simple)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
