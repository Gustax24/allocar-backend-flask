from marshmallow import Schema, fields, validate

class RatingCreateSchema(Schema):
    booking_id = fields.UUID(required=True)
    to_user_id = fields.UUID(required=True)
    stars = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.String(required=False, allow_none=True)

class RatingOutSchema(Schema):
    id = fields.UUID()
    from_user_id = fields.UUID()
    to_user_id = fields.UUID()
    booking_id = fields.UUID()
    stars = fields.Integer()
    comment = fields.String(allow_none=True)
    created_at = fields.DateTime()
