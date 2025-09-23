from math import radians, sin, cos, sqrt, asin

EARTH_RADIUS_KM = 6371.0

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Distance Haversine en kilomètres.
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS_KM * c

def estimate_duration_min(distance_km: float, speed_kmh: float = 50.0) -> int:
    """
    Durée estimée en minutes pour une distance (km) à vitesse moyenne (km/h).
    """
    if speed_kmh <= 0:
        speed_kmh = 50.0
    return int((distance_km / speed_kmh) * 60)

def clamp(v: float, vmin: float, vmax: float) -> float:
    return max(vmin, min(v, vmax))
