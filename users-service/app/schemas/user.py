from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length = 3, max_length = 20, description = "Your username")
    email: Optional[EmailStr] = Field(None, description = "Your email")
    first_name: Optional[str] = Field(None, min_length=2, max_length=30)
    second_name: Optional[str] = Field(None, min_length=2, max_length=30)
    
class UserCreate(UserBase):
    password: str = Field(..., min_length = 5, max_length = 20)
    
class UserUpdate(BaseModel):
    
    username: Optional[str] = Field(None, min_length = 3, max_length = 20, description = "Your username")
    first_name: Optional[str] = Field(None, min_length=2, max_length=30)
    second_name: Optional[str] = Field(None, min_length=2, max_length=30)
    email: Optional[EmailStr] = Field(None, min_length = 5, max_length = 100, description = "Your email") 
    password: Optional[str] = Field(None, min_length = 5, max_length = 20)
    
class UserResponse(UserBase):
    id: int = Field(..., description = "User unique ID")
    is_active: bool = Field(..., description = "Is user active")
    is_superuser: bool
    created_at: datetime = Field(..., description = "User registration date")
    
    model_config = ConfigDict(from_attributes=True)    