from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps
from common.errors import APIError

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper

def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt() or {}
            if claims.get("role") not in roles:
                raise APIError("forbidden", "Forbidden", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
