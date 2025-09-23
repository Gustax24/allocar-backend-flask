import os
from datetime import timedelta
from pathlib import Path


import settings.env  # noqa: F401

BASE_DIR = Path(__file__).resolve().parent

def _pg_uri():
    return (
        f"postgresql+psycopg2://{os.getenv('DB_USER','allocar')}:{os.getenv('DB_PASSWORD','allocar')}"
        f"@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/{os.getenv('DB_NAME','allocar')}"
    )

def _sqlite_uri():
    # Fichier allocar.db à la racine (à côté de app.py/config.py)
    return f"sqlite:///{(BASE_DIR / 'allocar.db').as_posix()}"

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_jwt")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=6)
    PROPAGATE_EXCEPTIONS = True

    # CORS
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

    # Redis / Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # Rate limit
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "60 per minute")

    # OTP / Reset
    OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "600"))
    OTP_RESEND_SECONDS = int(os.getenv("OTP_RESEND_SECONDS", "60"))
    OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

    RESET_TOKEN_TTL_SECONDS = int(os.getenv("RESET_TOKEN_TTL_SECONDS", "900"))
    OTP_EMAIL_TEMPLATE = os.getenv("OTP_EMAIL_TEMPLATE", "templates/email/otp.html")
    RESET_EMAIL_TEMPLATE = os.getenv("RESET_EMAIL_TEMPLATE", "templates/email/reset_otp.html")
    REQUIRE_VERIF_FOR_LOGIN = os.getenv("REQUIRE_VERIF_FOR_LOGIN", "false").lower() == "true"

    # S3
    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    S3_BUCKET = os.getenv("S3_BUCKET", "allocar")
    S3_REGION = os.getenv("S3_REGION", "us-east-1")
    S3_SECURE = os.getenv("S3_SECURE", "false").lower() == "true"

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # SQLite en dev, pas besoin de psycopg2
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLITE_URL", _sqlite_uri())

class ProductionConfig(BaseConfig):
    DEBUG = False
    # Postgres en prod
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", _pg_uri())

def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    return ProductionConfig if env == "production" else DevelopmentConfig
