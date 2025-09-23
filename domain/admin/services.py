from flask_jwt_extended import create_access_token, create_refresh_token
from common.errors import APIError
from common.security import verify_password
from domain.users.repository import get_user_by_email, get_user_by_phone
from .repository import list_users, trips_overview, kyc_pending
from domain.kyc.services import admin_review

def admin_login(identifier, password):
    u = get_user_by_email(identifier) or get_user_by_phone(identifier)
    if not u or u.role != "admin":
        raise APIError("forbidden", "Accès admin refusé", 403)
    if not u.password_hash or not verify_password(password, u.password_hash):
        raise APIError("invalid_credentials", "Identifiants invalides", 401)
    access = create_access_token(identity=str(u.id), additional_claims={"role": "admin"})
    refresh = create_refresh_token(identity=str(u.id))
    return {"access_token": access, "refresh_token": refresh, "user": u}

def admin_list_users(query=None, status=None):
    return list_users(query, status)

def admin_trips_overview():
    return trips_overview()

def admin_list_kyc_pending():
    return kyc_pending()

def admin_review_kyc(doc_id, reviewer_id, approve, notes):
    return admin_review(doc_id, reviewer_id, approve, notes)
