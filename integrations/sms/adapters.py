from .client import SMSClient

def send_otp_sms(phone_e164: str, code: str) -> bool:
    try:
        cli = SMSClient()
        res = cli.send(phone_e164, f"Votre code AlloCar est {code}")
        print(f"Votre code OTP est {code}")
        return True if res else False
    except Exception:
        return False
