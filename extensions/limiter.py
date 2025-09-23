from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # on lira depuis app.config au init_app
)

def init_app(app):
    # Applique la limite définie dans la config (ex: "60 per minute")
    default_rule = app.config.get("RATELIMIT_DEFAULT")
    if default_rule:
        limiter._default_limits = [default_rule]
    limiter.init_app(app)
