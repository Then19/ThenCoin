from uuid import UUID

from fastapi import APIRouter, Query, Depends

from app.repositories.users import UserAuthRepository, get_auth_repository
from app.schemas.users.user_token import UserAuthToken

router = APIRouter(prefix='/auth')


@router.get('/get_new_token', response_model=UserAuthToken)
async def gen_new_token(
        user_id: UUID = Query(..., alias='userId'),

        auth_repository: UserAuthRepository = Depends(get_auth_repository)
) -> UserAuthToken:
    """Генерация нового токена для пользователя __Только для разработки__"""
    return await auth_repository.create_new_tokens(user_id)

