import asyncpg

from app.repositories import BasePostgresRepository
from app.repositories.users import UserAuthRepository
from app.schemas.users.user import UserCard, UserRegisterModel
from app.schemas.users.user_token import UserAuthToken


class UserService:
    user_auth_repository: UserAuthRepository
    _postgresql: asyncpg.Connection
    pg_transaction = BasePostgresRepository.transaction

    def __init__(self, auth_repository: UserAuthRepository, postgresql: asyncpg.Connection):
        self.user_auth_repository = auth_repository
        self._postgresql = postgresql

    @pg_transaction
    async def register_new_user(self, user: UserRegisterModel) -> UserAuthToken:
        """Создаем нового пользователя, выдаем токены"""
        user: UserCard = user.create_user_card_model()
        await self.user_auth_repository.create_new_card(user)
        return await self.user_auth_repository.create_new_tokens(user.user_id)

    async def refresh_tokens(self, refresh_token: str) -> UserAuthToken:
        """Получить новую пару токенов"""
        return await self.user_auth_repository.refresh_tokens(refresh_token)
