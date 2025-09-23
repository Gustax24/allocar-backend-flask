from marshmallow import Schema, fields, validate

class WalletOutSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID()
    balance = fields.Float()
    currency = fields.String()

class WalletTopupSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=100))
    method = fields.String(required=True)

class WalletWithdrawSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=100))
    channel = fields.String(required=True)
