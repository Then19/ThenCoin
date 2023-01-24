from typing import Generator

from fastapi import Request

from app.databases.postgresql import get_user_pg_connection
from app.repositories.users import UserAuthRepository
from app.service.user_service import UserService


async def get_user_service(request: Request) -> Generator[UserService, None, None]:
    async with get_user_pg_connection(request) as conn:
        yield UserService(
            auth_repository=UserAuthRepository(conn),
            postgresql=conn
        )
