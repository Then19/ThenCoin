from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import constr, conset

from app.schemas import BaseModel
from app.schemas.users.user_role import UserRole


class UserCard(BaseModel):
    user_id: UUID
    roles: conset(item_type=UserRole)

    user_name: constr(min_length=4, max_length=16)
    email: Optional[constr(max_length=64, regex='%@%')]
    photo: Optional[UUID]

    created_at: datetime
