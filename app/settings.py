from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    application_name: str = "then19"
    sentry_dsn: Optional[str]

    postgresql_dsn: str
    clickhouse_dsn: str

    sentry_tracer_rate: float = 0.5

    access_token_lifetime = 24 * 60 * 60

    refresh_token_lifetime = 10 * 24 * 60 * 60


settings = Settings()
