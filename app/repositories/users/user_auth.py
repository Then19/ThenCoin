from typing import Optional
from uuid import UUID

import asyncpg
from fastapi import HTTPException
from app.repositories._base import BasePostgresRepository
from app.schemas.users.user import UserCard
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
