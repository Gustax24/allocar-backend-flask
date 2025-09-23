from datetime import datetime, timezone
import uuid


def now_utc():
    return datetime.now(timezone.utc)

def parse_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(str(value))
