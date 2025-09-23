from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.responses import ok
from common.utils import parse_uuid
from .schemas import WalletOutSchema, WalletTopupSchema, WalletWithdrawSchema
from .services import get_wallet, topup_wallet, withdraw_wallet

blp = Blueprint("wallet", __name__, description="User wallet")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, WalletOutSchema)
def get_wallet_route():
    uid = get_jwt_identity()
    return get_wallet(parse_uuid(uid))

@blp.route("/topup", methods=["POST"])
@jwt_required()
@blp.arguments(WalletTopupSchema)
@blp.response(200, WalletOutSchema)
def topup_route(payload):
    uid = get_jwt_identity()
    return topup_wallet(parse_uuid(uid), payload["amount"], payload["method"])

@blp.route("/withdraw", methods=["POST"])
@jwt_required()
@blp.arguments(WalletWithdrawSchema)
@blp.response(200, WalletOutSchema)
def withdraw_route(payload):
    uid = get_jwt_identity()
    return withdraw_wallet(parse_uuid(uid), payload["amount"], payload["channel"])
