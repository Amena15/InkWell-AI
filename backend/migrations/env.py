import asyncio
from logging.config import fileConfig
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from alembic import context

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set up Python loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the models and config
from app.core.config import settings
from app.database import Base

# Import all models to ensure they are registered with SQLAlchemy
from app.models import User, Project, Document, DocumentVersion, DocumentComment  # noqa: F401

# Set the target metadata
target_metadata = Base.metadata

# Get the database URL from environment variables
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)


def do_run_migrations(connection: Connection) -> None:
    """Run migrations in 'online' mode.

    :param connection: SQLAlchemy connection
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario, we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations are not supported with async SQLAlchemy")
else:
    asyncio.run(run_migrations_online())
