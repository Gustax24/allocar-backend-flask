import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(to_email: str, subject: str, html_body: str, text_body: str | None = None) -> bool:
    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", "587"))
    user = os.getenv("EMAIL_HOST_USER")
    password = os.getenv("EMAIL_HOST_PASSWORD")
    use_tls = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
    use_ssl = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
    debug = os.getenv("MAIL_DEBUG", "0") == "1"

    if not user or not password:
        print("[MAIL] EMAIL_HOST_USER / EMAIL_HOST_PASSWORD manquants")
        return False

    sender = os.getenv("DEFAULT_FROM_EMAIL", user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body or "", "html", "utf-8"))

    try:
        if use_ssl:
            # Port recommandé pour SSL direct = 465
            with smtplib.SMTP_SSL(host, port) as server:
                if debug: server.set_debuglevel(1)
                server.login(user, password)
                server.sendmail(sender, [to_email], msg.as_string())
        else:
            # STARTTLS recommandé pour Gmail = 587
            with smtplib.SMTP(host, port) as server:
                if debug: server.set_debuglevel(1)
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(user, password)
                server.sendmail(sender, [to_email], msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[MAIL] Auth error: {e}")
        print("→ Vérifie que tu utilises un App Password (2FA activée) et la bonne adresse EMAIL_HOST_USER.")
        return False
    except Exception as e:
        print(f"[MAIL] Error sending mail to {to_email}: {e}")
        return False