from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import constr, conset

from app.schemas import BaseModel
from app.schemas.users.user_role import UserRole


class UserCard(BaseModel):
    user_id: UUID
    roles: conset(item_type=UserRole)

    user_name: Optional[constr(max_length=32)]
    email: Optional[constr(max_length=64, regex='%@%')]
    photo: Optional[UUID]

    created_at: datetime


class UserRegisterModel(BaseModel):
    user_name: Optional[constr(max_length=32)]

    email: Optional[constr(max_length=64, regex='%@%')]

    def create_user_card_model(self):
        return UserCard(
            user_id=uuid4(),
            roles={UserRole.USER},
            email=self.email,
            user_name=self.user_name,
            created_at=datetime.now().astimezone()
        )
