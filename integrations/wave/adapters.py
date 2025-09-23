from .client import WaveClient

def wave_init(amount_xof: float, msisdn: str, metadata: dict | None = None) -> dict:
    cli = WaveClient()
    res = cli.create_payment_intent(amount_xof, msisdn, metadata)
    if res.get("mock"):
        return {"provider_ref": res["provider_ref"], "checkout_url": f"https://mock.wave.ci/checkout/{res['provider_ref']}"}
    # Adapter au format interne
    provider_ref = res.get("id") or res.get("reference") or res.get("provider_ref")
    checkout = res.get("checkout_url") or f"https://wave.com/checkout/{provider_ref}"
    return {"provider_ref": provider_ref, "checkout_url": checkout}
