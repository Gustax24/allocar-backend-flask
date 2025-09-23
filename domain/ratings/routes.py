from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from common.utils import parse_uuid
from .schemas import RatingCreateSchema, RatingOutSchema
from .services import add_rating, list_user_ratings

blp = Blueprint("ratings", __name__, description="User ratings")

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(RatingCreateSchema)
@blp.response(201, RatingOutSchema)
def create_rating(payload):
    uid = get_jwt_identity()
    return add_rating(parse_uuid(uid), payload["booking_id"], payload["to_user_id"], payload["stars"], payload.get("comment"))

@blp.route("/user/<uuid:user_id>", methods=["GET"])
@blp.response(200, RatingOutSchema(many=True))
def list_for_user_route(user_id):
    return list_user_ratings(user_id)
