from decimal import Decimal
from common.errors import APIError
from .repository import get_or_create_wallet, add_txn, save

def get_wallet(user_id):
    return get_or_create_wallet(user_id)

def topup_wallet(user_id, amount: float, method: str):
    if amount <= 0:
        raise APIError("validation_error", "Montant invalide", 400)
    w = get_or_create_wallet(user_id)
    w.balance = (w.balance or 0) + Decimal(str(amount))
    save(w)
    add_txn(w.id, "credit", amount, "topup", ref=method)
    return w

def withdraw_wallet(user_id, amount: float, channel: str):
    w = get_or_create_wallet(user_id)
    if amount <= 0 or w.balance < amount:
        raise APIError("insufficient_funds", "Solde insuffisant", 400)
    w.balance = (w.balance or 0) - Decimal(str(amount))
    save(w)
    add_txn(w.id, "debit", amount, "payout", ref=channel)
    return w
