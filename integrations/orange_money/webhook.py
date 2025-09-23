from flask_smorest import Blueprint
from flask import request
from .client import OrangeMoneyClient
from domain.payments.services import handle_webhook
from common.errors import APIError

blp = Blueprint("om_webhook", __name__, description="Orange Money webhook")

@blp.route("/payments/webhook/orange", methods=["POST"])
def om_webhook():
    raw = request.get_data()
    sig = request.headers.get("X-OM-Signature")
    if not OrangeMoneyClient.verify_signature(raw, sig):
        raise APIError("webhook_invalid_signature", "Invalid signature", 400)
    payload = request.get_json() or {}
    provider_ref = payload.get("provider_ref") or payload.get("id")
    status = payload.get("status")
    if status not in ("paid","failed"):
        return {"ok": True}
    p = handle_webhook("orange", provider_ref, status, sig)
    return {"id": str(p.id), "status": p.status}
