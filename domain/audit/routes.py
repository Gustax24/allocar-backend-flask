from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from .schemas import AuditOutSchema
from .services import list_audit

blp = Blueprint("audit", __name__, description="Audit logs")

def require_admin():
    claims = get_jwt() or {}
    if claims.get("role") != "admin":
        from common.errors import APIError
        raise APIError("forbidden", "Admin requis", 403)

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, AuditOutSchema(many=True))
def audit_list():
    require_admin()
    return list_audit()
