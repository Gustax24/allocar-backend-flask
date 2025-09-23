from app import app as flask_app
from extensions.celery import celery_app, init_celery

init_celery(flask_app)

import domain.users.tasks      # noqa
import domain.promos.tasks     # noqa
import domain.trips.tasks      # noqa
import domain.payments.tasks   # noqa
import domain.wallet.tasks     # noqa
import domain.messages.tasks   # noqa
import domain.kyc.tasks        # noqa
import domain.reports.tasks    # noqa
import domain.disputes.tasks   # noqa
import domain.ratings.tasks    # noqa
import domain.admin.tasks      # noqa

if __name__ == "__main__":
    celery_app.start()
