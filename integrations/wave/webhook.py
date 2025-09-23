from flask_smorest import Blueprint
from flask import request
from .client import WaveClient
from common.errors import APIError
from domain.payments.services import handle_webhook

blp = Blueprint("wave_webhook", __name__, description="Wave webhook")

@blp.route("/payments/webhook/wave", methods=["POST"])
def wave_webhook():
    raw = request.get_data()
    sig = request.headers.get("X-Wave-Signature")
    if not WaveClient.verify_signature(raw, sig):
        raise APIError("webhook_invalid_signature", "Invalid signature", 400)
    payload = request.get_json() or {}
    provider_ref = payload.get("provider_ref") or payload.get("id")
    status = payload.get("status")
    if status not in ("paid","failed"):
        return {"ok": True}  # ignore autres statuts
    p = handle_webhook("wave", provider_ref, status, sig)
    return {"id": str(p.id), "status": p.status}
