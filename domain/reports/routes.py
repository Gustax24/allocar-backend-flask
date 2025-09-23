from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from .schemas import PeriodQuerySchema, FinanceReportSchema, UsageReportSchema
from .services import finance_report, usage_report

blp = Blueprint("reports", __name__, description="Reports & dashboards")

def require_admin():
    claims = get_jwt() or {}
    if claims.get("role") != "admin":
        from common.errors import APIError
        raise APIError("forbidden", "Admin requis", 403)

@blp.route("/finance", methods=["GET"])
@jwt_required()
@blp.arguments(PeriodQuerySchema, location="query")
@blp.response(200, FinanceReportSchema)
def report_finance(query):
    require_admin()
    return finance_report(query.get("date_from"), query.get("date_to"))

@blp.route("/usage", methods=["GET"])
@jwt_required()
@blp.arguments(PeriodQuerySchema, location="query")
@blp.response(200, UsageReportSchema)
def report_usage(query):
    require_admin()
    return usage_report(query.get("date_from"), query.get("date_to"))
