import os, time, requests

STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_BASE = "https://api.stripe.com/v1"
DEFAULT_TIMEOUT = 12

class StripeClient:
    def __init__(self, secret_key: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.key = secret_key or STRIPE_KEY
        self.timeout = timeout

    def create_payment_intent(self, amount_xof: float, currency: str = "xof", metadata: dict | None = None) -> dict:
        if not self.key:
            return {"mock": True, "client_secret": f"pi_{int(time.time())}_secret_mock", "id": f"pi_{int(time.time())}"}
        url = f"{STRIPE_BASE}/payment_intents"
        # Stripe attend des cents : XOF n’a pas de décimales → amount en unités
        data = {
            "amount": int(amount_xof),
            "currency": currency,
            "metadata[app]": "AlloCar"
        }
        if metadata:
            for k, v in metadata.items():
                data[f"metadata[{k}]"] = v
        r = requests.post(url, data=data, auth=(self.key, ""), timeout=self.timeout)
        r.raise_for_status()
        return r.json()
