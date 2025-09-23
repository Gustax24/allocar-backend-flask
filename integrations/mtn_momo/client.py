import os, time, requests, hmac, hashlib

MTN_BASE_URL = os.getenv("MTN_BASE_URL", "https://sandbox.momodeveloper.mtn.com")
MTN_API_KEY  = os.getenv("MTN_API_KEY")
MTN_SECRET   = os.getenv("MTN_SECRET", "dev_secret")
DEFAULT_TIMEOUT = 12

class MTNMoMoClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url or MTN_BASE_URL
        self.api_key = api_key or MTN_API_KEY
        self.timeout = timeout

    def request_to_pay(self, amount_xof: float, customer_msisdn: str, metadata: dict | None = None) -> dict:
        if not self.api_key:
            return {"mock": True, "status": "created", "provider_ref": f"mtn_{int(time.time())}"}
        url = f"{self.base_url}/collection/v1_0/requesttopay"
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        payload = {"amount": str(int(amount_xof)), "currency": "XOF", "payer": {"partyIdType":"MSISDN","partyId": customer_msisdn}}
        payload.update(metadata or {})
        r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        # Dans MoMo, l'ID est souvent transmis via un header Location ou X-Reference-Id
        pref = r.headers.get("X-Reference-Id") or f"mtn_{int(time.time())}"
        return {"provider_ref": pref}

    @staticmethod
    def sign_payload(raw_body: bytes) -> str:
        secret = (MTN_SECRET or "dev_secret").encode("utf-8")
        import hashlib, hmac
        return hmac.new(secret, raw_body, hashlib.sha256).hexdigest()

    @staticmethod
    def verify_signature(raw_body: bytes, provided_sig: str) -> bool:
        expected = MTNMoMoClient.sign_payload(raw_body)
        return hmac.compare_digest(expected, provided_sig or "")
