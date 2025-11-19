from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Optional
from fastapi import status, HTTPException

from ..models.user import User
from ..schemas.auth import LoginResponse
from ..schemas.user import UserResponse, UserCreate, UserUpdate
from ..repositories.user_repository import UserRepository
from ..core.security import hash_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)

    async def register_user(self, user_data: UserCreate) -> UserResponse:

        username_existing = await self.user_repository.get_by_username(user_data.username)
        if username_existing:
            raise ValueError("Username already taken")

        if user_data.email:
            email_existing = await self.user_repository.get_by_email(user_data.email)
            if email_existing:
                raise ValueError("Email already registered")

        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

        user = await self.user_repository.create(user_dict)
        return UserResponse.model_validate(user)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
        
        update_data = user_data.model_dump(exclude_unset = True)
        
        if 'password' in update_data:
            update_data['hashed_password'] = hash_password(update_data.pop('password'))
        
        updated_user = await self.user_repository.update(user_id, update_data
                                                         )
        return UserResponse.model_validate(updated_user)
