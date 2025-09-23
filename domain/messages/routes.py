from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.responses import ok
from common.utils import parse_uuid
from .schemas import MessageCreateSchema, MessageOutSchema, MessageQuerySchema
from .services import list_messages, post_message

blp = Blueprint("messages", __name__, description="Booking messages")

@blp.route("/<uuid:booking_id>", methods=["GET"])
@jwt_required()
@blp.arguments(MessageQuerySchema, location="query")
@blp.response(200, MessageOutSchema(many=True))
def list_route(query, booking_id):
    uid = get_jwt_identity()
    return list_messages(parse_uuid(uid), booking_id, limit=query.get("limit", 50), before=query.get("before"))

@blp.route("/<uuid:booking_id>", methods=["POST"])
@jwt_required()
@blp.arguments(MessageCreateSchema)
@blp.response(201, MessageOutSchema)
def create_route(payload, booking_id):
    uid = get_jwt_identity()
    return post_message(parse_uuid(uid), booking_id, payload.get("type","text"), payload["content"])
