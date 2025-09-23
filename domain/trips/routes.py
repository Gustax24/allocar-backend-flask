from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.responses import ok
from common.errors import APIError
from common.utils import parse_uuid
from .schemas import TripCreateSchema, TripUpdateSchema, TripOutSchema, TripStopInSchema, TripStopOutSchema, TripSearchQuerySchema
from .services import (
    create_trip_service, update_trip_service, delete_trip_service,
    publish_trip_service, cancel_trip_service, add_stops_service,
    list_stops_service, list_my_trips_service, search_trips_service
)
from .repository import get as get_trip
from extensions.db import db

blp = Blueprint("trips", __name__, description="Trips & Search")

# Driver space
@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(TripCreateSchema)
@blp.response(201, TripOutSchema)
def create_trip(payload):
    uid = get_jwt_identity()
    return create_trip_service(parse_uuid(uid), payload)

@blp.route("/mine", methods=["GET"])
@jwt_required()
@blp.response(200, TripOutSchema(many=True))
def my_trips():
    uid = get_jwt_identity()
    status = None  # could read from query args with blp.arguments if needed
    return list_my_trips_service(parse_uuid(uid), status=status)

@blp.route("/<uuid:trip_id>", methods=["GET"])
@blp.response(200, TripOutSchema)
def get_trip_detail(trip_id):
    t = get_trip(trip_id)
    if not t:
        raise APIError("not_found", "Trajet introuvable", 404)
    return t

@blp.route("/<uuid:trip_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(TripUpdateSchema)
@blp.response(200, TripOutSchema)
def update_trip(payload, trip_id):
    uid = get_jwt_identity()
    return update_trip_service(uid, trip_id, payload)

@blp.route("/<uuid:trip_id>", methods=["DELETE"])
@jwt_required()
def delete_trip(trip_id):
    uid = get_jwt_identity()
    delete_trip_service(uid, trip_id)
    return ok({"deleted": True})

@blp.route("/<uuid:trip_id>/publish", methods=["POST"])
@jwt_required()
@blp.response(200, TripOutSchema)
def publish_trip(trip_id):
    uid = get_jwt_identity()
    return publish_trip_service(uid, trip_id)

@blp.route("/<uuid:trip_id>/cancel", methods=["POST"])
@jwt_required()
@blp.response(200, TripOutSchema)
def cancel_trip(trip_id):
    uid = get_jwt_identity()
    return cancel_trip_service(uid, trip_id)

@blp.route("/<uuid:trip_id>/stops", methods=["POST"])
@jwt_required()
@blp.arguments(TripStopInSchema(many=True))
@blp.response(201, TripStopOutSchema(many=True))
def add_stops(payload, trip_id):
    uid = get_jwt_identity()
    return add_stops_service(uid, trip_id, payload)

@blp.route("/<uuid:trip_id>/stops", methods=["GET"])
@jwt_required()
@blp.response(200, TripStopOutSchema(many=True))
def list_stops(trip_id):
    uid = get_jwt_identity()
    return list_stops_service(uid, trip_id)

# Public search
@blp.route("/search", methods=["GET"])
@blp.arguments(TripSearchQuerySchema, location="query")
@blp.response(200, TripOutSchema(many=True))
def search_trips(query_args):
    return search_trips_service(query_args)
