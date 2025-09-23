from .client import OrangeMoneyClient

def om_init(amount_xof: float, msisdn: str, metadata: dict | None = None) -> dict:
    cli = OrangeMoneyClient()
    res = cli.create_checkout(amount_xof, msisdn, metadata)
    if res.get("mock"):
        return {"provider_ref": res["provider_ref"], "checkout_url": f"https://mock.om.ci/checkout/{res['provider_ref']}"}
    provider_ref = res.get("id") or res.get("reference") or res.get("provider_ref")
    checkout = res.get("checkout_url") or f"https://om.orange.ci/checkout/{provider_ref}"
    return {"provider_ref": provider_ref, "checkout_url": checkout}
