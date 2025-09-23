from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from common.responses import ok
from common.utils import parse_uuid
from .schemas import (
    PromoCreateSchema, PromoUpdateSchema, PromoOutSchema,
    PromoValidateSchema, PromoValidationResultSchema
)
from .services import (
    admin_create_promo, admin_update_promo, admin_delete_promo, admin_list_promos,
    validate_promo_for_user, consume_promo
)

blp = Blueprint("promos", __name__, description="Promotions & coupons")

def require_admin():
    claims = get_jwt() or {}
    if claims.get("role") != "admin":
        from common.errors import APIError
        raise APIError("forbidden", "Admin requis", 403)

# Admin CRUD
@blp.route("/admin", methods=["GET"])
@jwt_required()
@blp.response(200, PromoOutSchema(many=True))
def list_admin():
    require_admin(); return admin_list_promos()

@blp.route("/admin", methods=["POST"])
@jwt_required()
@blp.arguments(PromoCreateSchema)
@blp.response(201, PromoOutSchema)
def create_admin(payload):
    require_admin(); return admin_create_promo(payload)

@blp.route("/admin/<uuid:promo_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(PromoUpdateSchema)
@blp.response(200, PromoOutSchema)
def update_admin(payload, promo_id):
    require_admin(); return admin_update_promo(promo_id, payload)

@blp.route("/admin/<uuid:promo_id>", methods=["DELETE"])
@jwt_required()
def delete_admin(promo_id):
    require_admin(); admin_delete_promo(promo_id); return ok({"deleted": True})

# Validation/consommation
@blp.route("/validate", methods=["POST"])
@jwt_required()
@blp.arguments(PromoValidateSchema)
@blp.response(200, PromoValidationResultSchema)
def validate_route(payload):
    uid = get_jwt_identity()
    # On peut optionnellement récupérer le montant via la booking
    amount = 0.0
    if payload.get("booking_id"):
        from domain.bookings.repository import get as get_booking
        b = get_booking(payload["booking_id"])
        amount = float(b.amount_total) if b else 0.0
    return validate_promo_for_user(payload["code"], parse_uuid(uid), amount)

@blp.route("/consume", methods=["POST"])
@jwt_required()
@blp.arguments(PromoValidateSchema)
def consume_route(payload):
    uid = get_jwt_identity()
    okk = consume_promo(payload["code"], parse_uuid(uid), payload.get("booking_id"))
    return ok({"consumed": okk})
