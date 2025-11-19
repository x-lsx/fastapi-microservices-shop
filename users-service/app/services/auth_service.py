from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password
from app.schemas.auth import LoginRequest
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def login_user(self, data: LoginRequest):
        user = await self.repo.get_by_username(data.username)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        return {
            "id": user.id,
            "username": str(user.username),
            "is_superuser": user.is_superuser
        }
