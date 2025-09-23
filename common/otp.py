import json, time, random, string
from flask import current_app
from extensions.cache import cache

def _otp_key(purpose, channel, identifier):
    # purpose: "verify_email" | "verify_phone" | "reset"
    return f"otp:{purpose}:{channel}:{identifier}"

def _attempts_key(purpose, channel, identifier):
    return f"otp_attempts:{purpose}:{channel}:{identifier}"

def _cooldown_key(purpose, channel, identifier):
    return f"otp_cooldown:{purpose}:{channel}:{identifier}"

def _gen_code(n=6):
    return "".join(str(random.randint(0,9)) for _ in range(n))

def _gen_token(n=48):
    # token opaque, stocké en redis
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(n))

def _ttl():
    return int(current_app.config.get("OTP_TTL_SECONDS", 600))

def _cooldown():
    return int(current_app.config.get("OTP_RESEND_SECONDS", 60))

def _max_attempts():
    return int(current_app.config.get("OTP_MAX_ATTEMPTS", 5))

def set_otp(purpose: str, channel: str, identifier: str) -> str:
    """
    Génère + stocke un OTP (avec cooldown). Retourne le code.
    purpose: verify_email|verify_phone|reset
    channel: email|phone|sms (ici on utilisera "email" ou "sms")
    """
    cd_key = _cooldown_key(purpose, channel, identifier)
    if cache.client.get(cd_key):
        # trop tôt pour renvoyer
        raise RuntimeError("otp_resend_too_soon")

    code = _gen_code(6)
    data = {"code": code, "purpose": purpose, "channel": channel, "id": identifier, "ts": int(time.time())}
    cache.client.set(_otp_key(purpose, channel, identifier), json.dumps(data), ex=_ttl())
    cache.client.set(_attempts_key(purpose, channel, identifier), 0, ex=_ttl())
    cache.client.set(cd_key, 1, ex=_cooldown())
    return code

def verify_otp(purpose: str, channel: str, identifier: str, code: str) -> bool:
    raw = cache.client.get(_otp_key(purpose, channel, identifier))
    if not raw:
        return False
    data = json.loads(raw)
    attempts_key = _attempts_key(purpose, channel, identifier)
    attempts = int(cache.client.get(attempts_key) or 0)
    if attempts >= _max_attempts():
        return False
    if str(data.get("code")) != str(code):
        cache.client.incr(attempts_key)
        cache.client.expire(attempts_key, _ttl())
        return False
    # succès → purge
    cache.client.delete(_otp_key(purpose, channel, identifier))
    cache.client.delete(attempts_key)
    return True

# Wrappers existants pour la vérif du compte
def set_otp_for_email(email: str) -> str:
    return set_otp("verify_email", "email", email)

def set_otp_for_phone(phone: str) -> str:
    return set_otp("verify_phone", "sms", phone)

def verify_email_otp(email: str, code: str) -> bool:
    return verify_otp("verify_email", "email", email, code)

def verify_phone_otp(phone: str, code: str) -> bool:
    return verify_otp("verify_phone", "sms", phone, code)

# Reset: générique
def set_reset_otp(identifier: str, channel: str) -> str:
    # channel doit être "email" ou "sms"
    return set_otp("reset", channel, identifier)

def verify_reset_otp(identifier: str, channel: str, code: str) -> bool:
    return verify_otp("reset", channel, identifier, code)

# Reset token (post-vérification OTP)
def _reset_token_key(identifier: str, token: str):
    return f"reset_token:{identifier}:{token}"

def issue_reset_token(identifier: str) -> str:
    token = _gen_token()
    ttl = int(current_app.config.get("RESET_TOKEN_TTL_SECONDS", 900))
    cache.client.set(_reset_token_key(identifier, token), 1, ex=ttl)
    return token

def consume_reset_token(identifier: str, token: str) -> bool:
    key = _reset_token_key(identifier, token)
    if cache.client.get(key):
        cache.client.delete(key)
        return True
    return False
