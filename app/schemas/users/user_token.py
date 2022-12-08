from random import choice
from string import ascii_letters
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import constr

from app.settings import settings

from app.schemas import BaseModel


class UserAuthToken(BaseModel):
    user_id: UUID
    access_token: constr(min_length=128, max_length=128)
    access_token_expires: datetime
    refresh_token: constr(min_length=128, max_length=128)
    refresh_token_expires: datetime
    created_at: datetime

    @staticmethod
    def generate_new_token():
        chars = ascii_letters + "0123456789"
        return ''.join(choice(chars) for _ in range(128))

    @staticmethod
    def create_new_tokens(user_id: UUID) -> "UserAuthToken":
        return UserAuthToken(
            user_id=user_id,
            access_token=UserAuthToken.generate_new_token(),
            access_token_expires=datetime.now().astimezone() + timedelta(seconds=settings.access_token_lifetime),
            refresh_token=UserAuthToken.generate_new_token(),
            refresh_token_expires=datetime.now().astimezone() + timedelta(seconds=settings.refresh_token_lifetime),
            created_at=datetime.now().astimezone()
        )
