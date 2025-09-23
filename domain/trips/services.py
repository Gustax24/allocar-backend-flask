from common.errors import APIError
from .repository import get, create_trip, update_trip, delete_trip, add_stops, list_stops, list_my_trips, search_trips

def ensure_driver_owns(trip_id, driver_id):
    t = get(trip_id)
    if not t or str(t.driver_id) != str(driver_id):
        raise APIError("not_found", "Trajet introuvable", 404)
    return t

def create_trip_service(driver_id, payload):
    return create_trip(driver_id, payload)

def update_trip_service(driver_id, trip_id, payload):
    t = ensure_driver_owns(trip_id, driver_id)
    if t.status in ("completed", "cancelled"):
        raise APIError("conflict", "Trajet non modifiable", 409)
    return update_trip(t, **payload)

def delete_trip_service(driver_id, trip_id):
    t = ensure_driver_owns(trip_id, driver_id)
    if t.status in ("ongoing", "completed"):
        raise APIError("conflict", "Trajet non supprimable", 409)
    delete_trip(t)

def publish_trip_service(driver_id, trip_id):
    t = ensure_driver_owns(trip_id, driver_id)
    return update_trip(t, status="published")

def cancel_trip_service(driver_id, trip_id):
    t = ensure_driver_owns(trip_id, driver_id)
    return update_trip(t, status="cancelled")

def add_stops_service(driver_id, trip_id, stops):
    t = ensure_driver_owns(trip_id, driver_id)
    return add_stops(t.id, stops)

def list_stops_service(driver_id, trip_id):
    t = ensure_driver_owns(trip_id, driver_id)
    return list_stops(t.id)

def list_my_trips_service(driver_id, status=None):
    return list_my_trips(driver_id, status=status)

def search_trips_service(params):
    return search_trips(params)
