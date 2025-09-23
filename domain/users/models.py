from extensions.db import db, UUIDMixin
from sqlalchemy.dialects.postgresql import UUID
from common.enums import UserRole
from datetime import datetime, timezone

class User(db.Model, UUIDMixin):
    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, nullable=True)
    phone = db.Column(db.String(32), unique=True, nullable=True)
    password_hash = db.Column(db.Text, nullable=True)

    first_name = db.Column(db.String(120), nullable=True)
    last_name  = db.Column(db.String(120), nullable=True)
    photo_url  = db.Column(db.String(512), nullable=True)

    role = db.Column(db.String(32), nullable=False, default=UserRole.USER.value)
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    is_phone_verified = db.Column(db.Boolean, default=False)

    rating_avg = db.Column(db.Numeric(3,2), nullable=False, default=0)
    rating_count = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "photo_url": self.photo_url,
            "role": self.role,
            "is_active": self.is_active,
            "is_email_verified": self.is_email_verified,
            "is_phone_verified": self.is_phone_verified,
            "rating_avg": float(self.rating_avg or 0),
            "rating_count": self.rating_count,
            "created_at": self.created_at if self.created_at else None,
        }

