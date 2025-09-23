from flask_smorest import Blueprint
from common.responses import ok
from common.errors import APIError
from common.utils import parse_uuid
from .schemas import RegisterSchema, LoginSchema, UserOutSchema, OTPRequestSchema, OTPVerifySchema
from .services import register_user, authenticate, request_otp_for_user, verify_otp_and_mark
from extensions.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity, create_refresh_token, create_access_token, get_jwt
from datetime import datetime, timezone
from common.jwt_blocklist import revoke
from extensions.s3 import get_s3_client
from flask import current_app
from .schemas import (
    RequestResetSchema, VerifyResetOTPSchema, ResetPasswordSchema, ChangePasswordSchema
)
from .services import (
    request_password_reset, verify_reset_otp_and_issue_token,
    reset_password_with_token, change_password
)


blp = Blueprint("users", __name__, description="Users & Auth")

@blp.route("/auth/register", methods=["POST"])
@blp.arguments(RegisterSchema)
@blp.response(201, UserOutSchema)
def register(payload):
    user = register_user(
        email=payload.get("email"),
        phone=payload.get("phone"),
        password=payload["password"],
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
    )
    return user.to_dict()

@blp.route("/auth/login", methods=["POST"])
@blp.arguments(LoginSchema)
def login(payload):
    user = authenticate(payload["identifier"], payload["password"])
    access = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh = create_refresh_token(identity=str(user.id))
    return ok({"access_token": access, "refresh_token": refresh, "user": user.to_dict()})


@blp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def token_refresh():
    uid = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role") or "user"
    access = create_access_token(identity=str(uid), additional_claims={"role": role})
    return ok({"access_token": access})

@blp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    j = get_jwt()
    exp = int(j.get("exp", 0)) - int(datetime.now(timezone.utc).timestamp())
    revoke(j.get("jti"), max(exp, 0))
    return ok({"logout": True})


@blp.route("/auth/request-otp", methods=["POST"])
@blp.arguments(OTPRequestSchema)
def request_otp_public(payload):
    from .repository import get_user_by_email, get_user_by_phone
    user = None
    if payload.get("email"):
        user = get_user_by_email(payload["email"])
    if not user and payload.get("phone"):
        user = get_user_by_phone(payload["phone"])
    if not user:
        # Réponse générique pour éviter l’énumération
        return ok({"sent": True})
    request_otp_for_user(user, payload.get("email"), payload.get("phone"))
    return ok({"sent": True})

@blp.route("/auth/verify-otp", methods=["POST"])
@blp.arguments(OTPVerifySchema)
def verify_otp(payload):
    # Trouve l’utilisateur par identifiant côté channel
    from .repository import get_user_by_email, get_user_by_phone
    if payload["channel"] == "email":
        user = get_user_by_email(payload["identifier"])
    elif payload["channel"] == "phone":
        user = get_user_by_phone(payload["identifier"])
    else:
        raise APIError("validation_error", "Canal invalide", 400)

    if not user:
        raise APIError("not_found", "Utilisateur introuvable", 404)

    verify_otp_and_mark(user, payload["channel"], payload["identifier"], payload["code"])
    return ok({
        "email_verified": user.is_email_verified,
        "phone_verified": user.is_phone_verified
    })


@blp.route("/auth/password/request-reset", methods=["POST"])
@blp.arguments(RequestResetSchema)
def password_request_reset(payload):
    request_password_reset(payload["identifier"], payload.get("channels", ["email"]))
    return ok({"sent": True})

@blp.route("/auth/password/verify-reset-otp", methods=["POST"])
@blp.arguments(VerifyResetOTPSchema)
def password_verify_reset_otp(payload):
    token = verify_reset_otp_and_issue_token(payload["identifier"], payload["channel"], payload["code"])
    return ok({"reset_token": token})

@blp.route("/auth/password/reset", methods=["POST"])
@blp.arguments(ResetPasswordSchema)
def password_reset(payload):
    reset_password_with_token(payload["identifier"], payload["reset_token"], payload["new_password"])
    return ok({"reset": True})

@blp.route("/auth/password/change", methods=["POST"])
@jwt_required()
@blp.arguments(ChangePasswordSchema)
def password_change(payload):
    uid = get_jwt_identity()
    change_password(uid, payload["old_password"], payload["new_password"])
    return ok({"changed": True})


@blp.route("/me", methods=["GET"])
@jwt_required()
def me():
    uid = get_jwt_identity()
    from .models import User
    user = db.session.get(User, parse_uuid(uid))
    if not user:
        raise APIError("not_found", "User not found", 404)
    return ok(user.to_dict())

@blp.route("/me/photo", methods=["POST"])
@jwt_required()
def me_photo_presign():
    uid = get_jwt_identity()
    s3 = get_s3_client(current_app)
    bucket = current_app.config.get("S3_BUCKET")
    key = f"users/{uid}/photo.jpg"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": key, "ContentType": "image/jpeg"},
        ExpiresIn=3600,
    )
    return ok({"upload_url": url, "key": key})
