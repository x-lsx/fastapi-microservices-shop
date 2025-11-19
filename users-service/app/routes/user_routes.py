from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from ..core.database import get_db
from ..schemas.user import UserResponse, UserCreate
from ..services.user_service import UserService
from ..core.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix = "/users", tags = ["users"])

@router.post("/register", response_model = UserResponse, status_code = status.HTTP_200_OK)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    try:
        return await service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user = Depends(get_current_user)):
    """Получение данных текущего пользователя"""
    return current_user