from extensions.db import db
from sqlalchemy import desc
from .models import AuditLog

def add(actor_type, actor_id, action, entity, entity_id=None, meta=None):
    a = AuditLog(actor_type=actor_type, actor_id=str(actor_id) if actor_id else None,
                 action=action, entity=entity, entity_id=str(entity_id) if entity_id else None, meta=meta or {})
    db.session.add(a); db.session.commit(); return a

def list_recent(limit=200):
    return db.session.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
