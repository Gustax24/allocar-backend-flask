from extensions.db import db
from sqlalchemy import desc
from .models import Dispute

def create(**kwargs):
    d = Dispute(**kwargs)
    db.session.add(d); db.session.commit(); return d

def get(d_id):
    return db.session.get(Dispute, d_id)

def save(entity):
    db.session.commit(); return entity

def list_by_user(user_id, limit=100):
    return db.session.query(Dispute).filter(Dispute.opened_by == user_id).order_by(desc(Dispute.created_at)).limit(limit).all()

def list_all(limit=200):
    return db.session.query(Dispute).order_by(desc(Dispute.created_at)).limit(limit).all()
