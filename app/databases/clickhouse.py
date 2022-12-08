from contextlib import asynccontextmanager
from typing import Optional

import asynch

from app.settings import settings

_pool = None  # type: Optional[asynch.pool.Pool]


@asynccontextmanager
async def get_pool() -> asynch.pool.Pool:
    global _pool

    if _pool is None:
        _pool = await asynch.create_pool(dsn=settings.clickhouse_dsn)

    yield _pool


async def is_online() -> bool:
    async with get_pool() as pool:  # type: asynch.pool.Pool
        async with pool.acquire() as connection:  # type: asynch.connection.Connection
            async with connection.cursor() as cursor:  # type: asynch.connection.Cursor
                await cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result == (1,)


async def close():
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
