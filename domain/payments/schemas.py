from marshmallow import Schema, fields, validate

class PaymentInitSchema(Schema):
    booking_id = fields.UUID(required=True)
    method = fields.String(required=True, validate=validate.OneOf(["wave","orange","mtn","card","wallet"]))
    customer_msisdn = fields.String(required=False, allow_none=True)  # E.164 pour wave/orange/mtn

class PaymentOutSchema(Schema):
    id = fields.UUID()
    booking_id = fields.UUID()
    user_id = fields.UUID()
    method = fields.String()
    provider_ref = fields.String(allow_none=True)
    amount = fields.Float()
    currency = fields.String()
    status = fields.String()
    created_at = fields.DateTime()

class PaymentWebhookSchema(Schema):
    provider_ref = fields.String(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["paid","failed"]))
