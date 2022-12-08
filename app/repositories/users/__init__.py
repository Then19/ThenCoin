from typing import Generator
from fastapi import Request

from app.repositories import get_repository
from app.repositories.users.user_auth import UserAuthRepository


async def get_auth_repository(request: Request) -> Generator[UserAuthRepository, None, None]:
    async with get_repository(UserAuthRepository, request) as repo:
        yield repo
