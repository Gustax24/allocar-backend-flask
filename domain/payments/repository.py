from extensions.db import db
from .models import Payment

def get(payment_id):
    return db.session.get(Payment, payment_id)

def get_by_provider_ref(pref):
    return db.session.query(Payment).filter(Payment.provider_ref == pref).first()

def create_for_booking(booking, user_id, method):
    p = Payment(
        booking_id=booking.id,
        user_id=user_id,
        method=method,
        amount=booking.amount_total,
        currency="XOF",
        status="init",
    )
    db.session.add(p)
    db.session.commit()
    return p

def save(entity):
    db.session.commit()
    return entity
