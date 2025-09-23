from extensions.db import db
from sqlalchemy import and_
from .models import Message

def list_for_booking(booking_id, limit=50, before=None):
    q = db.session.query(Message).filter(Message.booking_id == booking_id)
    if before:
        q = q.filter(Message.created_at < before)
    return q.order_by(Message.created_at.desc()).limit(limit).all()[::-1]

def create(booking_id, from_user_id, tp, content):
    m = Message(booking_id=booking_id, from_user_id=from_user_id, type=tp, content=content)
    db.session.add(m)
    db.session.commit()
    return m
