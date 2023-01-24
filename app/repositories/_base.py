import functools

import asyncpg


class BasePostgresRepository:
    _postgresql: asyncpg.Connection

    def __init__(
            self,
            _postgresql: asyncpg.Connection,
    ):
        self._postgresql = _postgresql

    def transaction(func):
        # noinspection PyCallingNonCallable
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            tr = self._postgresql.transaction()
            try:
                await tr.start()
                data = await func(self, *args, **kwargs)
            except Exception as ex:
                await tr.rollback()
                raise ex
            finally:
                await tr.commit()
            return data
        return wrapper
