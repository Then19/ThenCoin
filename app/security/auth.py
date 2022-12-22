from functools import wraps
from typing import Optional

import asyncpg
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

from app.databases import postgresql
from app.repositories.users.user_auth import UserAuthRepository
from app.schemas.users.user import UserCard
from app.schemas.users.user_role import UserRole

oauth_scheme = HTTPBearer()


async def get_user_by_token(
        token: str
) -> UserCard:
    async with postgresql.get_pool() as pool:  # type: asyncpg.Pool
        async with pool.acquire() as conn:  # type: asyncpg.Connection
            repo = UserAuthRepository(conn)
            user = await repo.get_user_by_token(token)

    if not user:
        raise HTTPException(403, detail="Forbidden error")

    return user


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth_scheme)) -> UserCard:
    return await get_user_by_token(token.credentials)


def allowed_roles(arg_name: str, roles: set[UserRole]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_card: Optional[UserCard] = kwargs.get(arg_name)
            if not user_card or not len(roles):
                return await func(*args, **kwargs)

            temp = roles.copy()
            temp.intersection_update(user_card.roles)

            if not len(temp):
                raise HTTPException(401, "Unauthorized error")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
