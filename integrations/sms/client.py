import os, requests

SMS_BASE_URL = os.getenv("SMS_BASE_URL")       # ex: https://api.smsprovider.ci
SMS_API_KEY  = os.getenv("SMS_API_KEY")        # clé API
SMS_SENDER   = os.getenv("SMS_SENDER", "AlloCar")

class SMSClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: int = 10):
        self.base_url = base_url or SMS_BASE_URL
        self.api_key = api_key or SMS_API_KEY
        self.timeout = timeout

    def send(self, to_e164: str, text: str) -> dict:
        if not self.base_url or not self.api_key:
            return {"mock": True, "success": True}
        url = f"{self.base_url.rstrip('/')}/messages"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"from": SMS_SENDER, "to": to_e164, "text": text}
        r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
