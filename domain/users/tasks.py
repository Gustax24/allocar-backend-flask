from extensions.celery import celery_app
from extensions.mail import send_mail
from integrations.sms.adapters import send_otp_sms
from flask import current_app

def _render_template(path: str, code: str) -> str:
    try:
        with current_app.open_resource(path) as f:
            html = f.read().decode("utf-8")
        return html.replace("{{CODE}}", str(code))
    except Exception:
        return f"<p>Votre code est <strong>{code}</strong>. Il expire dans 10 minutes.</p>"

@celery_app.task(name="users.send_email_otp")
def send_email_otp_task(email: str, code: str) -> bool:
    subject = "Votre code de vérification AlloCar"
    tpl = current_app.config.get("OTP_EMAIL_TEMPLATE", "templates/email/otp.html")
    html = _render_template(tpl, code)
    text = f"Votre code est {code}. Il expire dans 10 minutes."
    try:
        return send_mail(email, subject, html, text)
    except Exception:
        return False

@celery_app.task(name="users.send_sms_otp")
def send_sms_otp_task(phone: str, code: str) -> bool:
    try:
        return send_otp_sms(phone, code)
    except Exception:
        return False

@celery_app.task(name="users.send_email_reset_otp")
def send_email_reset_otp_task(email: str, code: str) -> bool:
    subject = "Réinitialisation de votre mot de passe AlloCar"
    tpl = current_app.config.get("RESET_EMAIL_TEMPLATE", "templates/email/reset_otp.html")
    html = _render_template(tpl, code)
    text = f"Votre code de réinitialisation est {code}. Il expire dans 10 minutes."
    try:
        return send_mail(email, subject, html, text)
    except Exception:
        return False
