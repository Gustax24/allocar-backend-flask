from datetime import datetime, timezone
from decimal import Decimal
from common.errors import APIError
from .repository import get_by_code, get, create, update, delete, usage_count, usage_count_by_user, add_usage, list_all

def admin_create_promo(payload):
    if get_by_code(payload["code"]):
        raise APIError("conflict", "Code promo déjà existant", 409)
    return create(**payload)

def admin_update_promo(promo_id, payload):
    p = get(promo_id)
    if not p: raise APIError("not_found", "Promo introuvable", 404)
    return update(p, **payload)

def admin_delete_promo(promo_id):
    p = get(promo_id)
    if not p: raise APIError("not_found", "Promo introuvable", 404)
    delete(p)

def admin_list_promos():
    return list_all()

def validate_promo_for_user(code: str, user_id, amount: float):
    p = get_by_code(code)
    if not p or p.status != "active":
        return {"valid": False, "reason": "invalid_code", "discount_amount": None}

    now = datetime.now(timezone.utc)
    if p.starts_at and now < p.starts_at:
        return {"valid": False, "reason": "not_started", "discount_amount": None}
    if p.ends_at and now > p.ends_at:
        return {"valid": False, "reason": "expired", "discount_amount": None}

    total_used = usage_count(p.id)
    if p.max_uses and total_used >= p.max_uses:
        return {"valid": False, "reason": "max_uses_reached", "discount_amount": None}

    used_by_user = usage_count_by_user(p.id, user_id)
    if p.per_user_limit and used_by_user >= p.per_user_limit:
        return {"valid": False, "reason": "per_user_limit_reached", "discount_amount": None}

    amt = Decimal(str(amount))
    if p.type == "amount":
        discount = min(amt, Decimal(str(p.value)))
    else:
        discount = (amt * Decimal(str(p.value))) / Decimal("100")

    return {"valid": True, "reason": None, "discount_amount": float(discount)}

def consume_promo(code: str, user_id, booking_id=None):
    p = get_by_code(code)
    if not p: raise APIError("not_found", "Promo introuvable", 404)
    add_usage(p.id, user_id, booking_id)
    return True
