from email_validator import validate_email, EmailNotValidError
from common.errors import APIError

def validate_email_or_400(email: str) -> str:
    try:
        return validate_email(email, check_deliverability=False).email
    except EmailNotValidError as e:
        raise APIError("validation_error", str(e), 400)
