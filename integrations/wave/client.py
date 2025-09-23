import os, time, hmac, hashlib, requests

WAVE_BASE_URL = os.getenv("WAVE_BASE_URL", "https://api.wave.com/v1")
WAVE_API_KEY  = os.getenv("WAVE_API_KEY")
WAVE_WEBHOOK_SECRET = os.getenv("WAVE_WEBHOOK_SECRET", "dev_secret")
DEFAULT_TIMEOUT = 12

class WaveClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url or WAVE_BASE_URL
        self.api_key = api_key or WAVE_API_KEY
        self.timeout = timeout

    def create_payment_intent(self, amount_xof: float, customer_msisdn: str, metadata: dict | None = None) -> dict:
        """
        Crée un intent de paiement. Retourne un provider_ref (transaction id).
        """
        if not self.api_key:
            # Mode mock
            return {"mock": True, "status": "created", "provider_ref": f"wave_{int(time.time())}"}
        url = f"{self.base_url}/payments"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"amount": int(amount_xof), "currency": "XOF", "msisdn": customer_msisdn, "metadata": metadata or {}}
        r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def sign_payload(raw_body: bytes) -> str:
        secret = (WAVE_WEBHOOK_SECRET or "dev_secret").encode("utf-8")
        return hmac.new(secret, raw_body, hashlib.sha256).hexdigest()

    @staticmethod
    def verify_signature(raw_body: bytes, provided_sig: str) -> bool:
        expected = WaveClient.sign_payload(raw_body)
        return hmac.compare_digest(expected, provided_sig or "")
