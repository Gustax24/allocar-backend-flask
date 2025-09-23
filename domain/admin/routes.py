from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from common.responses import ok
from common.errors import APIError
from common.utils import parse_uuid
from .schemas import AdminLoginSchema, AdminUserOutSchema
from .services import (
    admin_login, admin_list_users, admin_trips_overview,
    admin_list_kyc_pending, admin_review_kyc
)
from domain.trips.schemas import TripOutSchema
from domain.kyc.schemas import KYCOutSchema

blp = Blueprint("admin", __name__, description="Admin panel")

def require_admin():
    claims = get_jwt() or {}
    if claims.get("role") != "admin":
        raise APIError("forbidden", "Admin requis", 403)

@blp.route("/login", methods=["POST"])
@blp.arguments(AdminLoginSchema)
def login(payload):
    result = admin_login(payload["identifier"], payload["password"])
    u = result["user"]
    return ok({
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "user": {
            "id": str(u.id), "email": u.email, "phone": u.phone,
            "first_name": u.first_name, "last_name": u.last_name,
            "role": u.role, "created_at": u.created_at.isoformat() if u.created_at else None
        }
    })

@blp.route("/users", methods=["GET"])
@jwt_required()
@blp.response(200, AdminUserOutSchema(many=True))
def users_list():
    require_admin()
    from flask import request
    q = request.args.get("query")
    status = request.args.get("status")
    return admin_list_users(q, status)

@blp.route("/trips", methods=["GET"])
@jwt_required()
@blp.response(200, TripOutSchema(many=True))
def trips_list():
    require_admin()
    return admin_trips_overview()

@blp.route("/kyc/pending", methods=["GET"])
@jwt_required()
@blp.response(200, KYCOutSchema(many=True))
def kyc_pending():
    require_admin()
    return admin_list_kyc_pending()

@blp.route("/kyc/<uuid:doc_id>/approve", methods=["POST"])
@jwt_required()
@blp.response(200, KYCOutSchema)
def kyc_approve(doc_id):
    require_admin()
    uid = get_jwt_identity()
    return admin_review_kyc(doc_id, parse_uuid(uid), True, notes=None)

@blp.route("/kyc/<uuid:doc_id>/reject", methods=["POST"])
@jwt_required()
@blp.response(200, KYCOutSchema)
def kyc_reject(doc_id):
    require_admin()
    uid = get_jwt_identity()
    from flask import request
    notes = (request.get_json() or {}).get("notes")
    return admin_review_kyc(doc_id, parse_uuid(uid), False, notes=notes)
