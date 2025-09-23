from flask_smorest import Blueprint
from flask import request
from .client import MTNMoMoClient
from domain.payments.services import handle_webhook
from common.errors import APIError

blp = Blueprint("mtn_webhook", __name__, description="MTN MoMo webhook")

@blp.route("/payments/webhook/mtn", methods=["POST"])
def mtn_webhook():
    raw = request.get_data()
    sig = request.headers.get("X-MTN-Signature")
    if not MTNMoMoClient.verify_signature(raw, sig):
        raise APIError("webhook_invalid_signature", "Invalid signature", 400)
    payload = request.get_json() or {}
    provider_ref = payload.get("provider_ref") or payload.get("reference_id")
    status = payload.get("status")
    if status not in ("paid","failed"):
        return {"ok": True}
    p = handle_webhook("mtn", provider_ref, status, sig)
    return {"id": str(p.id), "status": p.status}
