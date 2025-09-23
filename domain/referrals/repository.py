from extensions.db import db
from sqlalchemy import func
from .models import Referral
from domain.users.models import User

def find_referrer_by_code(code: str):
    # Ici on choisit un code "USER-{first8uuid}". On mappe en recherchant un user dont id commence par...
    # Simplification: on stocke le code côté Referral seulement; en pratique, on aurait une table user_referral_code.
    # On tente de retrouver un user via email/phone == code en dernier recours (MVP).
    u = db.session.query(User).filter(User.email == code).first()
    if u: return u
    u = db.session.query(User).filter(User.phone == code).first()
    return u

def already_used_by_referee(referee_id):
    return db.session.query(Referral).filter(Referral.referee_id == referee_id).first()

def create(referrer_id, referee_id, code, bonus_referrer, bonus_referee):
    r = Referral(referrer_id=referrer_id, referee_id=referee_id, code_used=code,
                 bonus_referrer=bonus_referrer, bonus_referee=bonus_referee, status="granted")
    db.session.add(r); db.session.commit(); return r
