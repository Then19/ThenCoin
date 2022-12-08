import asyncpg


class BasePostgresRepository:
    _postgresql: asyncpg.Connection

    def __init__(
            self,
            _postgresql: asyncpg.Connection,
    ):
        self._postgresql = _postgresql
