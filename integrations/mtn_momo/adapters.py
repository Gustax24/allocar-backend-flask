from .client import MTNMoMoClient

def mtn_init(amount_xof: float, msisdn: str, metadata: dict | None = None) -> dict:
    cli = MTNMoMoClient()
    res = cli.request_to_pay(amount_xof, msisdn, metadata)
    provider_ref = res["provider_ref"]
    return {"provider_ref": provider_ref, "checkout_url": f"https://mock.mtn.ci/checkout/{provider_ref}"}
