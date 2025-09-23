from extensions.db import db
from .models import Vehicle

def list_by_user(user_id):
    return db.session.query(Vehicle).filter(Vehicle.user_id == user_id).order_by(Vehicle.created_at.desc()).all()

def get_by_id(v_id):
    return db.session.get(Vehicle, v_id)

def get_by_plate(plate: str):
    return db.session.query(Vehicle).filter(Vehicle.plate_number == plate).first()

def create(**kwargs) -> Vehicle:
    v = Vehicle(**kwargs)
    db.session.add(v)
    db.session.commit()
    return v

def update(entity: Vehicle, **kwargs) -> Vehicle:
    for k, v in kwargs.items():
        setattr(entity, k, v)
    db.session.commit()
    return entity

def delete(entity: Vehicle):
    db.session.delete(entity)
    db.session.commit()
