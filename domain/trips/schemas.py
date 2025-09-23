from marshmallow import Schema, fields, validate

class PointSchema(Schema):
    lat = fields.Float(required=True)
    lon = fields.Float(required=True)
    text = fields.String(required=True)

class TripCreateSchema(Schema):
    origin = fields.Nested(PointSchema, required=True)
    destination = fields.Nested(PointSchema, required=True)
    departure_time = fields.DateTime(required=True)
    arrival_eta = fields.DateTime(required=False, allow_none=True)
    price_per_seat = fields.Float(required=True)
    seats_available = fields.Integer(required=True, validate=validate.Range(min=1, max=8))
    luggage_policy = fields.String(required=False, allow_none=True)
    rules = fields.String(required=False, allow_none=True)
    allow_auto_accept = fields.Boolean(required=False, load_default=False)
    status = fields.String(required=False, load_default="published")

class TripUpdateSchema(Schema):
    departure_time = fields.DateTime()
    arrival_eta = fields.DateTime(allow_none=True)
    price_per_seat = fields.Float()
    seats_available = fields.Integer(validate=validate.Range(min=1, max=8))
    luggage_policy = fields.String(allow_none=True)
    rules = fields.String(allow_none=True)
    allow_auto_accept = fields.Boolean()
    status = fields.String(validate=validate.OneOf(["draft","published","ongoing","completed","cancelled"]))

class TripOutSchema(Schema):
    id = fields.UUID()
    driver_id = fields.UUID()
    origin_lat = fields.Float()
    origin_lon = fields.Float()
    origin_text = fields.String()
    destination_lat = fields.Float()
    destination_lon = fields.Float()
    destination_text = fields.String()
    departure_time = fields.DateTime()
    arrival_eta = fields.DateTime(allow_none=True)
    price_per_seat = fields.Float()
    seats_available = fields.Integer()
    luggage_policy = fields.String(allow_none=True)
    rules = fields.String(allow_none=True)
    allow_auto_accept = fields.Boolean()
    status = fields.String()
    created_at = fields.DateTime()

class TripStopInSchema(Schema):
    order = fields.Integer(required=True)
    lat = fields.Float(required=True)
    lon = fields.Float(required=True)
    label = fields.String(required=True)
    pickup_allowed = fields.Boolean(required=False, load_default=True)
    dropoff_allowed = fields.Boolean(required=False, load_default=True)

class TripStopOutSchema(Schema):
    id = fields.UUID()
    trip_id = fields.UUID()
    order = fields.Integer()
    lat = fields.Float()
    lon = fields.Float()
    label = fields.String()
    pickup_allowed = fields.Boolean()
    dropoff_allowed = fields.Boolean()

class TripSearchQuerySchema(Schema):
    from_lat = fields.Float(required=True)
    from_lon = fields.Float(required=True)
    to_lat = fields.Float(required=True)
    to_lon = fields.Float(required=True)
    date = fields.Date(required=False)  # filtre par jour
    radius_km = fields.Float(required=False, load_default=50.0)
    seats = fields.Integer(required=False, load_default=1)
    price_min = fields.Float(required=False)
    price_max = fields.Float(required=False)
