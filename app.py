import settings.env  # noqa: F401

from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from config import get_config

from extensions.db import db
from extensions.migrate import migrate
from extensions.jwt import jwt
from extensions.cache import cache
from extensions.limiter import limiter
from extensions.logger import init_logging
from extensions.socketio import socketio
from extensions.celery import init_celery

from common.errors import register_error_handlers

from domain.users.routes import blp as UsersBlueprint
from domain.vehicles.routes import blp as VehiclesBlueprint
from domain.trips.routes import blp as TripsBlueprint
from domain.bookings.routes import blp as BookingsBlueprint
from domain.payments.routes import blp as PaymentsBlueprint
from domain.wallet.routes import blp as WalletBlueprint
from domain.messages.routes import blp as MessagesBlueprint
from domain.ratings.routes  import blp as RatingsBlueprint
from domain.kyc.routes      import blp as KYCBlueprint
from domain.admin.routes    import blp as AdminBlueprint
from domain.promos.routes     import blp as PromosBlueprint
from domain.referrals.routes  import blp as ReferralsBlueprint
from domain.disputes.routes   import blp as DisputesBlueprint
from domain.reports.routes    import blp as ReportsBlueprint
from domain.audit.routes      import blp as AuditBlueprint

from integrations.wave.webhook import blp as WaveWebhookBlueprint
from integrations.orange_money.webhook import blp as OMWebhookBlueprint
from integrations.mtn_momo.webhook import blp as MTNWebhookBlueprint
from integrations.stripe.webhook import blp as StripeWebhookBlueprint

from realtime import events  # noqa: F401

def create_app():
    app = Flask(__name__)
    ConfigClass = get_config()
    app.config.from_object(ConfigClass)

    # CORS
    origins = app.config.get("CORS_ORIGINS") or ["*"]
    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    # API (OpenAPI)
    app.config["API_TITLE"] = "AlloCar API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.1.0"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    api = Api(app)

    # Extensions
    init_logging(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins=origins)
    init_celery(app)

    # Blueprints
    api.register_blueprint(UsersBlueprint, url_prefix="/api/v1/users")
    api.register_blueprint(VehiclesBlueprint, url_prefix="/api/v1/vehicles")
    api.register_blueprint(TripsBlueprint, url_prefix="/api/v1/trips")
    api.register_blueprint(BookingsBlueprint, url_prefix="/api/v1/bookings")
    api.register_blueprint(PaymentsBlueprint, url_prefix="/api/v1/payments")
    api.register_blueprint(WalletBlueprint, url_prefix="/api/v1/wallet")
    api.register_blueprint(MessagesBlueprint, url_prefix="/api/v1/messages")
    api.register_blueprint(RatingsBlueprint, url_prefix="/api/v1/ratings")
    api.register_blueprint(KYCBlueprint, url_prefix="/api/v1/kyc")
    api.register_blueprint(AdminBlueprint, url_prefix="/api/v1/admin")
    api.register_blueprint(PromosBlueprint, url_prefix="/api/v1/promos")
    api.register_blueprint(ReferralsBlueprint, url_prefix="/api/v1/referrals")
    api.register_blueprint(DisputesBlueprint, url_prefix="/api/v1/disputes")
    api.register_blueprint(ReportsBlueprint, url_prefix="/api/v1/reports")
    api.register_blueprint(AuditBlueprint, url_prefix="/api/v1/audit")

    # Webhooks
    api.register_blueprint(WaveWebhookBlueprint, url_prefix="/api/v1/integrations")
    api.register_blueprint(OMWebhookBlueprint,   url_prefix="/api/v1/integrations")
    api.register_blueprint(MTNWebhookBlueprint,  url_prefix="/api/v1/integrations")
    api.register_blueprint(StripeWebhookBlueprint, url_prefix="/api/v1/integrations")

    # Health
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    register_error_handlers(app)

    # Facultatif si extensions/celery a déjà include=...,
    # mais utile côté API pour éviter des surprises lors des .delay()
    import domain.users.tasks  # noqa: F401

    return app

app = create_app()

if __name__ == "__main__":
    import os
    debug = os.getenv("FLASK_ENV", "development").lower() != "production"
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        allow_unsafe_werkzeug=True,
        debug=debug,
    )
