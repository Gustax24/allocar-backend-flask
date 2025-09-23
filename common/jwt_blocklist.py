from extensions.cache import cache

BLOCKLIST_PREFIX = "jwt:blocklist:"

def revoke(jti: str, exp_seconds: int):
    if jti:
        cache.client.setex(f"{BLOCKLIST_PREFIX}{jti}", exp_seconds, "1")

def is_revoked(jti: str) -> bool:
    return cache.client.exists(f"{BLOCKLIST_PREFIX}{jti}") == 1
