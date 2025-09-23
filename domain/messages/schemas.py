from marshmallow import Schema, fields, validate

class MessageCreateSchema(Schema):
    type = fields.String(required=False, validate=validate.OneOf(["text","image"]), load_default="text")
    content = fields.String(required=True)

class MessageOutSchema(Schema):
    id = fields.UUID()
    booking_id = fields.UUID()
    from_user_id = fields.UUID()
    type = fields.String()
    content = fields.String()
    created_at = fields.DateTime()

class MessageQuerySchema(Schema):
    limit = fields.Integer(required=False, load_default=50)
    before = fields.DateTime(required=False)  # pagination temporelle (optionnelle)
