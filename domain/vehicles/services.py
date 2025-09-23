from common.errors import APIError
from .repository import list_by_user, get_by_id, get_by_plate, create, update, delete

def create_vehicle(user_id, payload):
    if get_by_plate(payload["plate_number"]):
        raise APIError("conflict", "Plaque déjà enregistrée", 409)
    return create(user_id=user_id, **payload)

def update_vehicle(user_id, vehicle_id, payload):
    v = get_by_id(vehicle_id)
    if not v or str(v.user_id) != str(user_id):
        raise APIError("not_found", "Véhicule introuvable", 404)
    return update(v, **payload)

def delete_vehicle(user_id, vehicle_id):
    v = get_by_id(vehicle_id)
    if not v or str(v.user_id) != str(user_id):
        raise APIError("not_found", "Véhicule introuvable", 404)
    delete(v)
