from marshmallow import Schema, fields, validate

class BookingCreateSchema(Schema):
    trip_id = fields.UUID(required=True)
    seats = fields.Integer(required=True, validate=validate.Range(min=1, max=8))

class BookingOutSchema(Schema):
    id = fields.UUID()
    trip_id = fields.UUID()
    passenger_id = fields.UUID()
    seats = fields.Integer()
    amount_total = fields.Float()
    status = fields.String()
    qr_code = fields.String(allow_none=True)
    created_at = fields.DateTime()

class BookingListQuerySchema(Schema):
    role = fields.String(required=True, validate=validate.OneOf(["passenger", "driver"]))
    status = fields.String(required=False)

class BookingActionSchema(Schema):
    # empty body acceptable
    _ = fields.String(load_default="")
