from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.responses import ok
from common.utils import parse_uuid
from .schemas import KYCSubmitSchema, KYCOutSchema
from .services import submit_kyc, my_kyc_status

blp = Blueprint("kyc", __name__, description="KYC")

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(KYCSubmitSchema)
@blp.response(201, KYCOutSchema)
def submit(payload):
    uid = get_jwt_identity()
    return submit_kyc(parse_uuid(uid), payload)

@blp.route("/status", methods=["GET"])
@jwt_required()
@blp.response(200, KYCOutSchema)
def status():
    uid = get_jwt_identity()
    return my_kyc_status(parse_uuid(uid))
