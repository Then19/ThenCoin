from typing import Optional
from uuid import UUID

import asyncpg
from fastapi import HTTPException
from app.repositories._base import BasePostgresRepository
from app.schemas.users.user import UserCard, UserRegisterModel
from app.schemas.users.user_token import UserAuthToken


class UserAuthRepository(BasePostgresRepository):
    _postgresql: asyncpg.Connection

    USER_CARD_TABLE = "users.user_card"
    USER_AUTH_TABLE = "users.user_auth_token"

    async def create_new_tokens(self, user_id: UUID) -> UserAuthToken:
        user_token = UserAuthToken.create_new_tokens(user_id=user_id)
        try:
            await self._postgresql.execute(
                f"""
                    INSERT INTO {self.USER_AUTH_TABLE}
                    ("user_id", "access_token", "access_token_expires",
                    "refresh_token", "refresh_token_expires", "created_at")
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (user_id) DO UPDATE
                    SET "user_id" = EXCLUDED."user_id",
                    "access_token" = EXCLUDED."access_token",
                    "access_token_expires" = EXCLUDED."access_token_expires",
                    "refresh_token" = EXCLUDED."refresh_token",
                    "refresh_token_expires" = EXCLUDED."refresh_token_expires",
                    "created_at" = EXCLUDED."created_at"
                """, user_token.user_id, user_token.access_token, user_token.access_token_expires,
                user_token.refresh_token, user_token.refresh_token_expires, user_token.created_at
            )
        except asyncpg.exceptions.ForeignKeyViolationError:
            raise HTTPException(403, 'Forbidden error')

        return user_token

    async def get_user_by_token(self, access_token: str) -> Optional[UserCard]:
        user_id = await self._postgresql.fetchval(f"""
            SELECT user_id FROM {self.USER_AUTH_TABLE}
            WHERE access_token = $1::text AND access_token_expires > NOW()
        """, access_token)

        if not user_id:
            return

        user = await self._postgresql.fetchrow(f"""
            SELECT * FROM {self.USER_CARD_TABLE}
            WHERE user_id = $1::UUID
        """, user_id)

        return UserCard.parse_obj(user) if user else None

    async def create_new_card(self, user: UserCard):
        try:
            await self._postgresql.execute(f"""
                INSERT INTO {self.USER_CARD_TABLE} VALUES ($1, $2, $3, $4, $5, $6)
            """, user.user_id, user.roles, user.user_name, user.email, user.photo, user.created_at)
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(422, 'User is exist')

    async def register_new_user(self, user: UserRegisterModel) -> UserAuthToken:
        async with self._postgresql.transaction():
            user: UserCard = user.get_user_card_model()
            await self.create_new_card(user)
            return await self.create_new_tokens(user.user_id)

    async def refresh_tokens(self, token: str) -> UserAuthToken:
        user_id: dict = await self._postgresql.fetchrow(
            f"""
            SELECT user_id FROM {self.USER_AUTH_TABLE}
            WHERE refresh_token = $1 AND refresh_token_expires > NOW()
            """, token)

        if not user_id:
            raise HTTPException(403, 'Forbidden error')

        return await self.create_new_tokens(user_id.get('user_id'))
