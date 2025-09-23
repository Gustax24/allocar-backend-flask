from extensions.db import db
from sqlalchemy import desc
from .models import KYCDocument

def create(user_id, payload):
    k = KYCDocument(user_id=user_id, **payload)
    db.session.add(k); db.session.commit(); return k

def latest_for_user(user_id):
    return db.session.query(KYCDocument).filter(KYCDocument.user_id == user_id).order_by(desc(KYCDocument.created_at)).first()

def list_pending(limit=100):
    return db.session.query(KYCDocument).filter(KYCDocument.status == "pending").order_by(KYCDocument.created_at.asc()).limit(limit).all()

def get(doc_id):
    return db.session.get(KYCDocument, doc_id)

def save(entity):
    db.session.commit(); return entity
