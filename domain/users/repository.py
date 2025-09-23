from extensions.db import db
from .models import User

def get_user_by_email(email: str) -> User | None:
    return db.session.query(User).filter(User.email == email).first()

def get_user_by_phone(phone: str) -> User | None:
    return db.session.query(User).filter(User.phone == phone).first()

def create_user(**kwargs) -> User:
    user = User(**kwargs)
    db.session.add(user)
    db.session.commit()
    return user
