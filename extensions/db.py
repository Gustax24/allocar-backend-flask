from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import MetaData
import uuid

# Conventions de nommage (Alembic friendly)
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# Mixin UUID pour toutes les tables
class UUIDMixin:
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
