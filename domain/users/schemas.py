from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required=False)
    phone = fields.String(required=False)
    password = fields.String(required=True, load_only=True)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)

class LoginSchema(Schema):
    identifier = fields.String(required=True)  # email ou phone
    password = fields.String(required=True, load_only=True)

class UserOutSchema(Schema):
    id = fields.UUID()
    email = fields.Email(allow_none=True)
    phone = fields.String(allow_none=True)
    first_name = fields.String(allow_none=True)
    last_name = fields.String(allow_none=True)
    photo_url = fields.String(allow_none=True)
    role = fields.String()
    is_active = fields.Boolean()
    is_email_verified = fields.Boolean()
    is_phone_verified = fields.Boolean()
    rating_avg = fields.Float()
    rating_count = fields.Integer()
    created_at = fields.DateTime()

class OTPRequestSchema(Schema):
    email = fields.Email(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True)

class OTPVerifySchema(Schema):
    channel = fields.String(required=True, validate=validate.OneOf(["email","phone"]))
    identifier = fields.String(required=True)  # email ou phone selon channel
    code = fields.String(required=True)

class RequestResetSchema(Schema):
    identifier = fields.String(required=True)  # email ou phone
    channels = fields.List(fields.String(validate=validate.OneOf(["email","sms"])), required=False, load_default=["email"])

class VerifyResetOTPSchema(Schema):
    identifier = fields.String(required=True)
    channel = fields.String(required=True, validate=validate.OneOf(["email","sms"]))
    code = fields.String(required=True)

class ResetPasswordSchema(Schema):
    identifier = fields.String(required=True)
    reset_token = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))

class ChangePasswordSchema(Schema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))


