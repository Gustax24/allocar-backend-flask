from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from common.responses import ok
from common.errors import APIError
from common.utils import parse_uuid
from .schemas import PaymentInitSchema, PaymentOutSchema, PaymentWebhookSchema
from .services import init_payment, handle_webhook

blp = Blueprint("payments", __name__, description="Payments (Wave mock)")

@blp.route("/init", methods=["POST"])
@jwt_required()
@blp.arguments(PaymentInitSchema)
def init_route(payload):
    uid = get_jwt_identity()
    result = init_payment(parse_uuid(uid), payload["booking_id"], payload["method"], payload.get("customer_msisdn"))
    return ok(result)

# Webhook public (signature simplifiée via header X-Mock-Signature)
@blp.route("/webhook/<string:provider>", methods=["POST"])
@blp.arguments(PaymentWebhookSchema)
@blp.response(200, PaymentOutSchema)
def webhook(payload, provider):
    signature = request.headers.get("X-Mock-Signature")
    # on pourrait vérifier le secret ici
    p = handle_webhook(provider, payload["provider_ref"], payload["status"], signature)
    return p
