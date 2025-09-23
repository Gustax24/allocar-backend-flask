from functools import wraps
from flask import request
from common.errors import APIError
from extensions.cache import cache

def idempotent(key_prefix: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            idem = request.headers.get("Idempotency-Key")
            if not idem:
                return fn(*args, **kwargs)
            key = f"idem:{key_prefix}:{idem}"
            if cache.client.get(key):
                raise APIError("idempotent_conflict", "Duplicate request", 409)
            try:
                return fn(*args, **kwargs)
            finally:
                cache.client.setex(key, 60 * 10, "1")
        return wrapper
    return decorator
