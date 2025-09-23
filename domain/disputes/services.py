from datetime import datetime, timezone
from common.errors import APIError
from .repository import create, get, save, list_by_user, list_all

def open_dispute(user_id, booking_id, category, description):
    return create(booking_id=booking_id, opened_by=user_id, category=category, description=description)

def my_disputes(user_id):
    return list_by_user(user_id)

def admin_list_disputes():
    return list_all()

def admin_update_dispute(doc_id, reviewer_id, status, resolution=None):
    d = get(doc_id)
    if not d: raise APIError("not_found", "Litige introuvable", 404)
    d.status = status
    d.resolution = resolution
    d.resolved_by = reviewer_id
    d.resolved_at = datetime.now(timezone.utc)
    save(d)
    return d
