import os, requests

FCM_KEY = os.getenv("FCM_SERVER_KEY")  # clé serveur FCM
FCM_URL = "https://fcm.googleapis.com/fcm/send"

class FCMClient:
    def __init__(self, server_key: str | None = None, timeout: int = 10):
        self.key = server_key or FCM_KEY
        self.timeout = timeout

    def send_to_token(self, token: str, title: str, body: str, data: dict | None = None) -> dict:
        if not self.key:
            return {"mock": True, "success": True}
        payload = {
            "to": token,
            "notification": {"title": title, "body": body},
            "data": data or {},
        }
        headers = {"Authorization": f"key={self.key}", "Content-Type": "application/json"}
        r = requests.post(FCM_URL, json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
