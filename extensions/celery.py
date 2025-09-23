from __future__ import annotations

import settings.env
import os
from celery import Celery
from flask import Flask

TASK_MODULES = [
    "domain.users.tasks",
    "domain.promos.tasks",
    "domain.trips.tasks",
    "domain.payments.tasks",
    "domain.wallet.tasks",
    "domain.messages.tasks",
    "domain.kyc.tasks",
    "domain.reports.tasks",
    "domain.disputes.tasks",
    "domain.ratings.tasks",
    "domain.admin.tasks",
]

celery_app = Celery("allocar", include=TASK_MODULES)

def init_celery(app: Flask) -> Celery:
    celery_app.conf.update(
        broker_url=app.config.get("CELERY_BROKER_URL", os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")),
        result_backend=app.config.get("CELERY_RESULT_BACKEND", os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")),
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone=app.config.get("CELERY_TIMEZONE", "UTC"),
        enable_utc=True,
        broker_connection_retry_on_startup=True,
    )

    class AppContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)  # 👈 important

    celery_app.Task = AppContextTask
    return celery_app