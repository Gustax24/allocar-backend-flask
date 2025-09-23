from marshmallow import Schema, fields

class AuditOutSchema(Schema):
    id = fields.UUID()
    actor_type = fields.String()
    actor_id = fields.String(allow_none=True)
    action = fields.String()
    entity = fields.String()
    entity_id = fields.String(allow_none=True)
    meta = fields.Dict(allow_none=True)
    created_at = fields.DateTime()
