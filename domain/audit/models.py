from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class AuditLog(db.Model, UUIDMixin):
    __tablename__ = "audit_logs"

    actor_type = db.Column(db.String(16), nullable=False)  # user|admin|system
    actor_id = db.Column(db.String(64), nullable=True)
    action = db.Column(db.String(64), nullable=False)
    entity = db.Column(db.String(64), nullable=False)
    entity_id = db.Column(db.String(64), nullable=True)
    meta = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
