from marshmallow import Schema, fields

class AdminLoginSchema(Schema):
    identifier = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

class AdminUserOutSchema(Schema):
    id = fields.UUID()
    email = fields.String(allow_none=True)
    phone = fields.String(allow_none=True)
    first_name = fields.String(allow_none=True)
    last_name = fields.String(allow_none=True)
    role = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()

class AdminUsersQuerySchema(Schema):
    query = fields.String(required=False)
    status = fields.String(required=False)  # active|inactive (optionnel)
