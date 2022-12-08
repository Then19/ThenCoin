from fastapi import APIRouter, HTTPException, Depends
from app.databases import postgresql, clickhouse
from app.schemas.users.user import UserCard
from app.schemas.users.user_role import UserRole
from app.security.auth import get_current_user, allowed_roles

router = APIRouter(prefix="/tools")


@router.get("/health")
async def health():
    if not postgresql.is_online():
        raise HTTPException(503, "Postgresql lezhit blyat'")
    if not clickhouse.is_online():
        raise HTTPException(503, "Clickhouse lezhit blyat'")
    return "OK"


@router.get('/me', response_model=UserCard)
@allowed_roles('user', {UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN, UserRole.OWNER})
async def get_user_info(user: UserCard = Depends(get_current_user)) -> UserCard:
    return user
