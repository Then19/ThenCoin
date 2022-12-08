from asyncio import sleep

import asynch
import sentry_sdk
from asynch.cursors import DictCursor
from app.settings import settings

from app.databases import clickhouse


class Logger:
    def __init__(self):
        pass

    def _get_insert_data(self) -> dict[str, list]:
        return {}

    async def insert_data_in_base(self, coon: asynch.connection.Connection):
        async with coon.cursor(cursor=DictCursor) as cursor:  # type: asynch.cursors.DictCursor
            for name, data in self._get_insert_data().items():
                await cursor.execute(
                    f"""
                        INSERT INTO {name}
                        VALUES
                    """, data
                )


logger = Logger()


async def start_log():
    while True:
        try:
            async with clickhouse.get_pool() as pool:  # type: asynch.pool.Pool
                async with pool.acquire() as conn:  # type: asynch.connection.Connection
                    await logger.insert_data_in_base(conn)
        except Exception as ex:
            if settings.sentry_dsn:
                sentry_sdk.capture_exception(ex)
            else:
                print(ex)

        await sleep(20)
