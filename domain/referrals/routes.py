from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from common.utils import parse_uuid
from .schemas import ReferralUseSchema, ReferralOutSchema
from .services import apply_referral

blp = Blueprint("referrals", __name__, description="Referral program")

@blp.route("/use", methods=["POST"])
@jwt_required()
@blp.arguments(ReferralUseSchema)
@blp.response(201, ReferralOutSchema)
def use_code(payload):
    uid = get_jwt_identity()
    return apply_referral(parse_uuid(uid), payload["code"])
