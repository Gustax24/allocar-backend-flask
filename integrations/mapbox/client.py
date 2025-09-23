import os, requests

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

class MapboxClient:
    def __init__(self, token: str | None = None, timeout: int = 10):
        self.token = token or MAPBOX_TOKEN
        self.timeout = timeout

    def route(self, origin: tuple[float, float], dest: tuple[float, float], profile: str = "driving") -> dict:
        if not self.token:
            raise RuntimeError("MAPBOX_TOKEN not configured")
        # lon,lat ; lon,lat
        o = f"{origin[1]},{origin[0]}"; d = f"{dest[1]},{dest[0]}"
        url = f"https://api.mapbox.com/directions/v5/mapbox/{profile}/{o};{d}"
        params = {"alternatives": "false", "geometries": "geojson", "overview": "full", "access_token": self.token}
        r = requests.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
