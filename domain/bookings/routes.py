from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.responses import ok
from common.utils import parse_uuid
from .schemas import BookingCreateSchema, BookingOutSchema, BookingListQuerySchema, BookingActionSchema
from .services import (
    create_booking, accept_booking, reject_booking, cancel_booking, checkin_booking,
    start_ride, end_ride, list_bookings_by_role
)
from .repository import get as get_booking

blp = Blueprint("bookings", __name__, description="Bookings flow")

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(BookingCreateSchema)
@blp.response(201, BookingOutSchema)
def create_booking_route(payload):
    uid = get_jwt_identity()
    return create_booking(parse_uuid(uid), payload["trip_id"], payload["seats"])

@blp.route("/<uuid:booking_id>", methods=["GET"])
@jwt_required()
@blp.response(200, BookingOutSchema)
def get_booking_route(booking_id):
    b = get_booking(booking_id)
    if not b:
        return ok({}, status=404)
    return b

@blp.route("", methods=["GET"])
@jwt_required()
@blp.arguments(BookingListQuerySchema, location="query")
@blp.response(200, BookingOutSchema(many=True))
def list_bookings_route(query):
    uid = get_jwt_identity()
    return list_bookings_by_role(parse_uuid(uid), query["role"], query.get("status"))

@blp.route("/<uuid:booking_id>/accept", methods=["POST"])
@jwt_required()
@blp.arguments(BookingActionSchema)
@blp.response(200, BookingOutSchema)
def accept_booking_route(_, booking_id):
    uid = get_jwt_identity()
    return accept_booking(parse_uuid(uid), booking_id)

@blp.route("/<uuid:booking_id>/reject", methods=["POST"])
@jwt_required()
@blp.arguments(BookingActionSchema)
@blp.response(200, BookingOutSchema)
def reject_booking_route(_, booking_id):
    uid = get_jwt_identity()
    return reject_booking(parse_uuid(uid), booking_id)

@blp.route("/<uuid:booking_id>/cancel", methods=["POST"])
@jwt_required()
@blp.arguments(BookingActionSchema)
@blp.response(200, BookingOutSchema)
def cancel_booking_route(_, booking_id):
    uid = get_jwt_identity()
    return cancel_booking((uid), booking_id)

@blp.route("/<uuid:booking_id>/checkin", methods=["POST"])
@jwt_required()
@blp.arguments(BookingActionSchema)
@blp.response(200, BookingOutSchema)
def checkin_route(_, booking_id):
    uid = get_jwt_identity()
    return checkin_booking(parse_uuid(uid), booking_id)

@blp.route("/<uuid:booking_id>/start-ride", methods=["POST"])
@jwt_required()
@blp.arguments(BookingActionSchema)
@blp.response(200, BookingOutSchema)
def start_ride_route(_, booking_id):
    uid = get_jwt_identity()
    return start_ride(parse_uuid(uid), booking_id)

@blp.route("/<uuid:booking_id>/end-ride", methods=["POST"])
@jwt_required()
@blp.arguments(BookingActionSchema)
@blp.response(200, BookingOutSchema)
def end_ride_route(_, booking_id):
    uid = get_jwt_identity()
    return end_ride(parse_uuid(uid), booking_id)
