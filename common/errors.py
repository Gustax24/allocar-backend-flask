from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(HTTPException):
    code = 400
    description = "API error"

    def __init__(self, code="bad_request", message=None, status_code=None, details=None):
        super().__init__(message or self.description)
        self.error_code = code
        self.details = details
        if status_code:
            self.code = status_code

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(e: APIError):
        resp = {
            "error": {
                "code": e.error_code,
                "message": str(e),
                "details": e.details or {},
            }
        }
        return jsonify(resp), e.code

    @app.errorhandler(HTTPException)
    def handle_http_exc(e: HTTPException):
        resp = {"error": {"code": "http_error", "message": e.description}}
        return jsonify(resp), e.code

    @app.errorhandler(Exception)
    def handle_any():
        app.logger.exception("Unhandled error")
        resp = {"error": {"code": "internal_error", "message": "Internal server error"}}
        return jsonify(resp), 500
