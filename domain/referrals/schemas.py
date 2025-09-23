from marshmallow import Schema, fields

class ReferralUseSchema(Schema):
    code = fields.String(required=True)  # code du parrain (ex: dérivé de son UUID)

class ReferralOutSchema(Schema):
    id = fields.UUID()
    referrer_id = fields.UUID()
    referee_id = fields.UUID()
    code_used = fields.String()
    bonus_referrer = fields.Float()
    bonus_referee = fields.Float()
    status = fields.String()
    created_at = fields.DateTime()
