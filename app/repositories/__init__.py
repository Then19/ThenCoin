from contextlib import asynccontextmanager
from typing import Type, Optional

import asyncpg
from fastapi import Request

from app.databases import postgresql
from app.repositories._base import BasePostgresRepository


@asynccontextmanager
async def get_repository(repo: Type, request: Optional[Request] = None):
    if issubclass(repo, BasePostgresRepository):
        if request is None:
            async with postgresql.get_pool() as pool:  # type: asyncpg.Pool
                async with pool.acquire() as conn:  # type: asyncpg.Connection
                    yield repo(conn)
        else:
            key = "postgresql_connection"
            if key in request.scope and not request.scope[key].is_closed():
                yield repo(request.scope[key])
            else:
                async with postgresql.get_pool() as pool:  # type: asyncpg.Pool
                    async with pool.acquire() as conn:  # type: asyncpg.Connection
                        request.scope[key] = conn
                        yield repo(conn)
                        del request.scope[key]
    else:
        raise TypeError("Invalid repository type")
