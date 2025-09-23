from decimal import Decimal
from common.errors import APIError
from .repository import find_referrer_by_code, already_used_by_referee, create
from domain.wallet.services import get_wallet, topup_wallet

BONUS_REFERRER = Decimal("500")  # XOF
BONUS_REFEREE  = Decimal("500")

def apply_referral(referee_id, code: str):
    if already_used_by_referee(referee_id):
        raise APIError("conflict", "Code parrain déjà utilisé", 409)
    referrer = find_referrer_by_code(code)
    if not referrer:
        raise APIError("not_found", "Code parrain invalide", 404)
    if str(referrer.id) == str(referee_id):
        raise APIError("validation_error", "Auto-parrainage interdit", 400)

    # Crédite les wallets
    topup_wallet(referrer.id, float(BONUS_REFERRER), "referral")
    topup_wallet(referee_id, float(BONUS_REFEREE), "referral")

    return create(referrer.id, referee_id, code, float(BONUS_REFERRER), float(BONUS_REFEREE))
