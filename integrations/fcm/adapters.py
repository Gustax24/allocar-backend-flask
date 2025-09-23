from .client import FCMClient

def notify_booking_status(token: str, status: str, booking_id: str) -> bool:
    try:
        cli = FCMClient()
        res = cli.send_to_token(token, "Statut réservation", f"Votre réservation est {status}.", {"booking_id": booking_id, "status": status})
        return True if res else False
    except Exception:
        return False
