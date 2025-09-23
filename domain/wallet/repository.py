from extensions.db import db
from .models import Wallet, WalletTxn

def get_or_create_wallet(user_id):
    w = db.session.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not w:
        w = Wallet(user_id=user_id, balance=0, currency="XOF")
        db.session.add(w)
        db.session.commit()
    return w

def add_txn(wallet_id, tp, amount, source, ref=None, status="done"):
    t = WalletTxn(wallet_id=wallet_id, type=tp, amount=amount, source=source, ref=ref, status=status)
    db.session.add(t); db.session.commit(); return t

def save(wallet):
    db.session.commit()
    return wallet
