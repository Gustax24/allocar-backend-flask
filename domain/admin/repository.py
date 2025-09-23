from extensions.db import db
from sqlalchemy import or_
from domain.users.models import User
from domain.trips.models import Trip
from domain.kyc.models import KYCDocument

def list_users(q=None, status=None, limit=200):
    qry = db.session.query(User)
    if q:
        like = f"%{q}%"
        qry = qry.filter(or_(User.email.ilike(like), User.phone.ilike(like), User.first_name.ilike(like), User.last_name.ilike(like)))
    if status == "active":
        qry = qry.filter(User.is_active == True)
    elif status == "inactive":
        qry = qry.filter(User.is_active == False)
    return qry.order_by(User.created_at.desc()).limit(limit).all()

def trips_overview(limit=200):
    return db.session.query(Trip).order_by(Trip.created_at.desc()).limit(limit).all()

def kyc_pending(limit=100):
    return db.session.query(KYCDocument).filter(KYCDocument.status == "pending").order_by(KYCDocument.created_at.asc()).limit(limit).all()
