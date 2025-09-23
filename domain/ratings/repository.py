from extensions.db import db
from sqlalchemy import func
from .models import Rating
from domain.users.models import User

def create(**kwargs):
    r = Rating(**kwargs)
    db.session.add(r)
    db.session.commit()
    return r

def list_for_user(user_id, limit=100):
    return db.session.query(Rating).filter(Rating.to_user_id == user_id).order_by(Rating.created_at.desc()).limit(limit).all()

def recompute_user_rating(to_user_id):
    agg = db.session.query(func.avg(Rating.stars), func.count(Rating.id)).filter(Rating.to_user_id == to_user_id).first()
    avg = float(agg[0] or 0)
    cnt = int(agg[1] or 0)
    u = db.session.get(User, to_user_id)
    if u:
        u.rating_avg = avg
        u.rating_count = cnt
        db.session.commit()
    return avg, cnt
