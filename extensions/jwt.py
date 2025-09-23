from flask_jwt_extended import JWTManager
from datetime import datetime, timezone
from common.jwt_blocklist import is_revoked

jwt = JWTManager()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    return is_revoked(jti)
