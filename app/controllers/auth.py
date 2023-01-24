from uuid import UUID

from fastapi import APIRouter, Query, Depends

from app.repositories.users import UserAuthRepository, get_auth_repository
from app.schemas.users.user import UserRegisterModel
from app.schemas.users.user_token import UserAuthToken
from app.service import UserService, get_user_service

router = APIRouter(prefix='/auth')


@router.get('/get_new_token', response_model=UserAuthToken)
async def gen_new_token(
        user_id: UUID = Query(..., alias='userId'),

        auth_repository: UserAuthRepository = Depends(get_auth_repository)
) -> UserAuthToken:
    """Генерация нового токена для пользователя __Только для разработки__"""
    return await auth_repository.create_new_tokens(user_id)


@router.get("/refresh_token")
async def generate_refresh_token(
        refresh_token: str = Query(..., alias="refreshToken", min_length=128, max_length=128),

        auth_repository: UserAuthRepository = Depends(get_auth_repository)
):
    """Генерирует новую пару токенов"""
    return await auth_repository.refresh_tokens(refresh_token)


@router.post('/register')
async def register_new_user(
        data: UserRegisterModel,

        user_service: UserService = Depends(get_user_service)
) -> UserAuthToken:
    return await user_service.register_new_user(data)
