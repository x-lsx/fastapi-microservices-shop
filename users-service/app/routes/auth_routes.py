from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from ..core.database import get_db
from ..schemas.auth import LoginResponse, LoginRequest
from ..services.auth_service import AuthService
from ..core.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix = "/auth", tags = ["auths"])

@router.post("/login", response_model = LoginResponse, status_code = status.HTTP_201_CREATED)
async def login_user(user_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login_user(user_data)

