import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
  fileConfig(config.config_file_name)

target_metadata = None


def _build_db_url() -> str:
  required = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
  missing = [k for k in required if not os.getenv(k)]
  if missing:
    raise RuntimeError(
      f'Missing required env vars for DB connection: {", ".join(missing)}'
    )
  return (
    f'postgresql+psycopg://'
    f'{os.environ["DB_USER"]}:{os.environ["DB_PASSWORD"]}'
    f'@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}'
    f'/{os.environ["DB_NAME"]}'
  )


def run_migrations_online() -> None:
  config.set_main_option('sqlalchemy.url', _build_db_url())
  connectable = engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix='sqlalchemy.',
    poolclass=pool.NullPool,
  )
  with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
      context.run_migrations()


if context.is_offline_mode():
  raise RuntimeError('Offline migrations are not supported in this project')

run_migrations_online()
