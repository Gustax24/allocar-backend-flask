import os, requests
from typing import List, Tuple

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org")

class OSRMClient:
    def __init__(self, base_url: str | None = None, timeout: int = 10):
        self.base_url = base_url or OSRM_BASE_URL
        self.timeout = timeout

    def route(self, coords: List[Tuple[float, float]], profile: str = "driving") -> dict:
        """
        coords: [(lon, lat), (lon, lat)]
        Retourne JSON OSRM (distance en mètres, duration en secondes, geometry, etc.)
        """
        if len(coords) < 2:
            raise ValueError("At least two coordinates required")
        coord_str = ";".join([f"{lon},{lat}" for (lon, lat) in coords])
        url = f"{self.base_url}/route/v1/{profile}/{coord_str}"
        params = {"overview": "full", "geometries": "geojson"}
        r = requests.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
