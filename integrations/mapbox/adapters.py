from .client import MapboxClient
from common.geo import estimate_duration_min, haversine_km

def estimate_trip_mapbox(origin: tuple[float, float], dest: tuple[float, float]) -> dict:
    try:
        cli = MapboxClient()
        data = cli.route(origin, dest)
        route = data["routes"][0]
        meters = route["distance"]
        seconds = route["duration"]
        return {
            "distance_km": meters / 1000.0,
            "duration_min": int(seconds / 60),
            "geometry": route.get("geometry")
        }
    except Exception:
        km = haversine_km(origin[0], origin[1], dest[0], dest[1])
        return {"distance_km": km, "duration_min": estimate_duration_min(km), "geometry": None}
