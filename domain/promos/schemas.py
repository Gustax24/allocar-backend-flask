from marshmallow import Schema, fields, validate

class PromoCreateSchema(Schema):
    code = fields.String(required=True)
    type = fields.String(required=True, validate=validate.OneOf(["amount","percent"]))
    value = fields.Float(required=True)
    max_uses = fields.Integer(required=True)
    per_user_limit = fields.Integer(required=True)
    starts_at = fields.DateTime(required=False, allow_none=True)
    ends_at = fields.DateTime(required=False, allow_none=True)
    status = fields.String(required=False, load_default="active")

class PromoUpdateSchema(Schema):
    type = fields.String(validate=validate.OneOf(["amount","percent"]))
    value = fields.Float()
    max_uses = fields.Integer()
    per_user_limit = fields.Integer()
    starts_at = fields.DateTime(allow_none=True)
    ends_at = fields.DateTime(allow_none=True)
    status = fields.String(validate=validate.OneOf(["active","disabled"]))

class PromoOutSchema(Schema):
    id = fields.UUID()
    code = fields.String()
    type = fields.String()
    value = fields.Float()
    max_uses = fields.Integer()
    per_user_limit = fields.Integer()
    starts_at = fields.DateTime(allow_none=True)
    ends_at = fields.DateTime(allow_none=True)
    status = fields.String()
    created_at = fields.DateTime()

class PromoValidateSchema(Schema):
    code = fields.String(required=True)
    booking_id = fields.UUID(required=False)  # pour contexte optionnel

class PromoValidationResultSchema(Schema):
    valid = fields.Boolean()
    reason = fields.String(allow_none=True)
    discount_amount = fields.Float(allow_none=True)
