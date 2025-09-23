from marshmallow import Schema, fields, validate

class VehicleCreateSchema(Schema):
    make = fields.String(required=True)
    model = fields.String(required=True)
    color = fields.String(required=False, allow_none=True)
    plate_number = fields.String(required=True)
    seats_total = fields.Integer(required=True, validate=validate.Range(min=1, max=8))
    comfort_level = fields.String(required=False, validate=validate.OneOf(["basic", "standard", "comfort"]), load_default="standard")
    year = fields.Integer(required=False, allow_none=True)

class VehicleUpdateSchema(Schema):
    make = fields.String()
    model = fields.String()
    color = fields.String(allow_none=True)
    seats_total = fields.Integer(validate=validate.Range(min=1, max=8))
    comfort_level = fields.String(validate=validate.OneOf(["basic", "standard", "comfort"]))
    year = fields.Integer()

class VehicleOutSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID()
    make = fields.String()
    model = fields.String()
    color = fields.String(allow_none=True)
    plate_number = fields.String()
    seats_total = fields.Integer()
    comfort_level = fields.String()
    year = fields.Integer(allow_none=True)
    verified = fields.Boolean()
    created_at = fields.DateTime()
