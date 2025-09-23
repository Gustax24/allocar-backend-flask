from extensions.db import db
from sqlalchemy import func
from .models import Promo, PromoUsage

def get_by_code(code: str):
    return db.session.query(Promo).filter(Promo.code == code).first()

def get(promo_id):
    return db.session.get(Promo, promo_id)

def create(**kwargs):
    p = Promo(**kwargs)
    db.session.add(p); db.session.commit(); return p

def update(entity: Promo, **kwargs):
    for k,v in kwargs.items(): setattr(entity, k, v)
    db.session.commit(); return entity

def delete(entity: Promo):
    db.session.delete(entity); db.session.commit()

def usage_count(promo_id):
    return db.session.query(func.count(PromoUsage.id)).filter(PromoUsage.promo_id == promo_id).scalar() or 0

def usage_count_by_user(promo_id, user_id):
    return db.session.query(func.count(PromoUsage.id)).filter(PromoUsage.promo_id == promo_id, PromoUsage.user_id == user_id).scalar() or 0

def add_usage(promo_id, user_id, booking_id=None):
    u = PromoUsage(promo_id=promo_id, user_id=user_id, booking_id=booking_id)
    db.session.add(u); db.session.commit(); return u

def list_all(limit=200):
    return db.session.query(Promo).order_by(Promo.created_at.desc()).limit(limit).all()
