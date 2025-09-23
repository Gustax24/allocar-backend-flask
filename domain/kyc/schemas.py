from marshmallow import Schema, fields, validate

class KYCSubmitSchema(Schema):
    doc_type = fields.String(required=True, validate=validate.OneOf(["cni","passport","permis"]))
    doc_number = fields.String(required=True)
    front_url = fields.String(required=True)
    back_url = fields.String(required=False, allow_none=True)

class KYCOutSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID()
    doc_type = fields.String()
    doc_number = fields.String()
    front_url = fields.String()
    back_url = fields.String(allow_none=True)
    status = fields.String()
    notes = fields.String(allow_none=True)
    reviewed_by = fields.UUID(allow_none=True)
    reviewed_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
