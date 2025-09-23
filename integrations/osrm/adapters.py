from .client import OSRMClient
from common.geo import estimate_duration_min

def estimate_trip_osrm(origin: tuple[float, float], dest: tuple[float, float]) -> dict:
    """
    Calcule distance/durée avec OSRM si dispo, sinon fallback estimation locale.
    origin=(lat, lon), dest=(lat, lon)
    """
    try:
        cli = OSRMClient()
        data = cli.route([(origin[1], origin[0]), (dest[1], dest[0])])
        route = data["routes"][0]
        meters = route["distance"]
        seconds = route["duration"]
        return {
            "distance_km": meters / 1000.0,
            "duration_min": int(seconds / 60),
            "geometry": route.get("geometry"),
        }
    except Exception:
        # fallback simple
        from common.geo import haversine_km
        km = haversine_km(origin[0], origin[1], dest[0], dest[1])
        return {"distance_km": km, "duration_min": estimate_duration_min(km), "geometry": None}
