from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Wallet(db.Model, UUIDMixin):
    __tablename__ = "wallets"

    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    balance = db.Column(db.Numeric(12,2), nullable=False, default=0)
    currency = db.Column(db.String(8), nullable=False, default="XOF")

    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class WalletTxn(db.Model, UUIDMixin):
    __tablename__ = "wallet_txns"

    wallet_id = db.Column(db.ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.String(16), nullable=False)   # credit|debit
    amount = db.Column(db.Numeric(12,2), nullable=False)
    source = db.Column(db.String(32), nullable=False) # refund|topup|payout|promo
    ref = db.Column(db.String(128), nullable=True)
    status = db.Column(db.String(16), nullable=False, default="done") # done|pending|failed
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
