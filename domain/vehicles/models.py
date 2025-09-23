from extensions.db import db, UUIDMixin
from datetime import datetime, timezone

class Vehicle(db.Model, UUIDMixin):
    __tablename__ = "vehicles"

    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    make = db.Column(db.String(120), nullable=False)          # marque
    model = db.Column(db.String(120), nullable=False)         # modèle
    color = db.Column(db.String(50), nullable=True)
    plate_number = db.Column(db.String(32), nullable=False, unique=True)
    seats_total = db.Column(db.Integer, nullable=False, default=4)
    comfort_level = db.Column(db.String(32), nullable=False, default="standard")  # basic|standard|comfort
    year = db.Column(db.Integer, nullable=True)
    verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
