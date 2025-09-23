from datetime import datetime, timezone
from common.errors import APIError
from .repository import create, latest_for_user, list_pending, get, save
from domain.audit.services import audit as audit_log

def submit_kyc(user_id, payload):
    return create(user_id, payload)

def my_kyc_status(user_id):
    return latest_for_user(user_id)

def admin_list_pending():
    return list_pending()

def admin_review(doc_id, reviewer_id, approve: bool, notes: str | None):
    k = get(doc_id)
    if not k:
        raise APIError("not_found", "Dossier KYC introuvable", 404)
    k.status = "approved" if approve else "rejected"
    k.notes = notes
    k.reviewed_by = reviewer_id
    k.reviewed_at = datetime.now(timezone.utc)
    save(k)
    audit_log("admin", reviewer_id, "kyc.review", "kyc", k.id,
              {"approved": approve, "notes": notes})
    return k
