import os, time, requests, hmac, hashlib

OM_BASE_URL = os.getenv("OM_BASE_URL", "https://api.orange.com/orange-money-webpay")
OM_API_KEY  = os.getenv("OM_API_KEY")
OM_SECRET   = os.getenv("OM_SECRET", "dev_secret")  # pour signature webhook (selon intégration locale)
DEFAULT_TIMEOUT = 12

class OrangeMoneyClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url or OM_BASE_URL
        self.api_key = api_key or OM_API_KEY
        self.timeout = timeout

    def create_checkout(self, amount_xof: float, customer_msisdn: str, metadata: dict | None = None) -> dict:
        if not self.api_key:
            return {"mock": True, "status": "created", "provider_ref": f"om_{int(time.time())}"}
        url = f"{self.base_url}/v1/payments"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"amount": int(amount_xof), "currency": "XOF", "msisdn": customer_msisdn, "metadata": metadata or {}}
        r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def sign_payload(raw_body: bytes) -> str:
        secret = (OM_SECRET or "dev_secret").encode("utf-8")
        return hmac.new(secret, raw_body, hashlib.sha256).hexdigest()

    @staticmethod
    def verify_signature(raw_body: bytes, provided_sig: str) -> bool:
        expected = OrangeMoneyClient.sign_payload(raw_body)
        return hmac.compare_digest(expected, provided_sig or "")
