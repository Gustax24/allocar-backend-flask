from marshmallow import Schema, fields

class PeriodQuerySchema(Schema):
    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False)

class FinanceReportSchema(Schema):
    total_payments = fields.Float()
    total_completed_bookings = fields.Integer()
    revenue_estimate = fields.Float()

class UsageReportSchema(Schema):
    trips_published = fields.Integer()
    bookings_created = fields.Integer()
    active_users = fields.Integer()
