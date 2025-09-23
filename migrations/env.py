from __future__ import with_statement
import os
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config

# Active la config logging *uniquement* si un fichier existe
if config.config_file_name and os.path.exists(config.config_file_name):
    fileConfig(config.config_file_name)

# Métadonnées SQLAlchemy exposées par Flask-Migrate
target_metadata = current_app.extensions["migrate"].db.metadata

def run_migrations_offline():
    url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = current_app.extensions["migrate"].db.engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()