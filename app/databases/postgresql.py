from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Request

import asyncpg

from app.settings import settings

_pool = None  # type: Optional[asyncpg.Pool]


@asynccontextmanager
async def get_pool() -> asyncpg.Pool:
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.postgresql_dsn,
            server_settings={
                "application_name": settings.application_name,
            },
            min_size=8,
            max_size=30,
        )

    yield _pool


@asynccontextmanager
async def get_conn() -> asyncpg.Connection:
    async with get_pool() as pool:  # type: asyncpg.Pool
        async with pool.acquire() as connection:  # type: asyncpg.Connection
            yield connection


async def is_online() -> bool:
    async with get_conn() as connection:
        result = await connection.is_closed()
        return result == 1


@asynccontextmanager
async def get_user_pg_connection(request: Request):
    key = "postgresql_connection"
    if key in request.scope and not request.scope[key].is_closed():
        yield request.scope[key]
    else:
        async with get_conn() as conn:  # type: asyncpg.Connection
            request.scope[key] = conn
            yield conn
            del request.scope[key]


async def close():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
