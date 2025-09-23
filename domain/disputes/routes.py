from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from common.utils import parse_uuid
from .schemas import DisputeCreateSchema, DisputeUpdateSchema, DisputeOutSchema
from .services import open_dispute, my_disputes, admin_list_disputes, admin_update_dispute

blp = Blueprint("disputes", __name__, description="Disputes & support")

def require_admin():
    claims = get_jwt() or {}
    if claims.get("role") != "admin":
        from common.errors import APIError
        raise APIError("forbidden", "Admin requis", 403)

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(DisputeCreateSchema)
@blp.response(201, DisputeOutSchema)
def create_dispute(payload):
    uid = get_jwt_identity()
    return open_dispute(parse_uuid(uid), payload["booking_id"], payload["category"], payload["description"])

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, DisputeOutSchema(many=True))
def list_my_disputes():
    uid = get_jwt_identity()
    return my_disputes(parse_uuid(uid))

# Admin
@blp.route("/admin", methods=["GET"])
@jwt_required()
@blp.response(200, DisputeOutSchema(many=True))
def list_admin():
    require_admin(); return admin_list_disputes()

@blp.route("/admin/<uuid:doc_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DisputeUpdateSchema)
@blp.response(200, DisputeOutSchema)
def update_admin(payload, doc_id):
    require_admin()
    uid = get_jwt_identity()
    return admin_update_dispute(doc_id, parse_uuid(uid), payload["status"], payload.get("resolution"))
