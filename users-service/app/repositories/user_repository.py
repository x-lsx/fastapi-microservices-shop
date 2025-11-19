from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..core.security import hash_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Optional[User]:
        """Возвращает Пользователя по USERNAME"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Возвращает Пользователя по ID"""
        result = await self.db.execute(select(User).where(User.id == user_id)) 
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Возвращает Пользователя по EMAIL"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Возвращает обновленного пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        forbidden_fields = {"id", "hashed_password", "created_at"}
        for field, value in user_data.items():
            if field in forbidden_fields:
                continue
            if hasattr(user, field):
                setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user