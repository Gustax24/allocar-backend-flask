from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.responses import ok
from common.errors import APIError
from common.utils import parse_uuid
from .schemas import VehicleCreateSchema, VehicleUpdateSchema, VehicleOutSchema
from .repository import list_by_user, get_by_id
from .services import create_vehicle, update_vehicle, delete_vehicle

blp = Blueprint("vehicles", __name__, description="Vehicles CRUD")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, VehicleOutSchema(many=True))
def my_vehicles():
    uid = get_jwt_identity()
    return list_by_user(parse_uuid(uid))

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(VehicleCreateSchema)
@blp.response(201, VehicleOutSchema)
def create_vehicle_route(payload):
    uid = get_jwt_identity()
    return create_vehicle(parse_uuid(uid), payload)

@blp.route("/<uuid:vehicle_id>", methods=["GET"])
@jwt_required()
@blp.response(200, VehicleOutSchema)
def get_vehicle(vehicle_id):
    v = get_by_id(vehicle_id)
    if not v or str(v.user_id) != get_jwt_identity():
        raise APIError("not_found", "Véhicule introuvable", 404)
    return v

@blp.route("/<uuid:vehicle_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(VehicleUpdateSchema)
@blp.response(200, VehicleOutSchema)
def update_vehicle_route(payload, vehicle_id):
    uid = get_jwt_identity()
    return update_vehicle(uid, vehicle_id, payload)

@blp.route("/<uuid:vehicle_id>", methods=["DELETE"])
@jwt_required()
def delete_vehicle_route(vehicle_id):
    uid = get_jwt_identity()
    delete_vehicle(uid, vehicle_id)
    return ok({"deleted": True})
