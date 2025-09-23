from .client import StripeClient

def stripe_init(amount_xof: float, metadata: dict | None = None) -> dict:
    cli = StripeClient()
    res = cli.create_payment_intent(amount_xof, "xof", metadata)
    if res.get("mock"):
        return {"provider_ref": res["id"], "client_secret": res["client_secret"]}
    return {"provider_ref": res["id"], "client_secret": res["client_secret"]}
