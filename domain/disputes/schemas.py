from marshmallow import Schema, fields

class DisputeCreateSchema(Schema):
    booking_id = fields.UUID(required=True)
    category = fields.String(required=True)
    description = fields.String(required=True)

class DisputeUpdateSchema(Schema):
    status = fields.String(required=True)      # in_review|resolved|rejected
    resolution = fields.String(required=False, allow_none=True)

class DisputeOutSchema(Schema):
    id = fields.UUID()
    booking_id = fields.UUID()
    opened_by = fields.UUID()
    category = fields.String()
    description = fields.String()
    status = fields.String()
    resolution = fields.String(allow_none=True)
    resolved_by = fields.UUID(allow_none=True)
    resolved_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
