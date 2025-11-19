from sqlalchemy import Integer, String, Boolean, func, DateTime
from sqlalchemy.orm import  Mapped, mapped_column
from datetime import datetime
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    username: Mapped[str] = mapped_column(String(100),nullable = False, unique=True)
    email: Mapped[str] = mapped_column(String(100),nullable = True, unique=True)
    first_name: Mapped[str] = mapped_column(String(40), nullable = True)
    second_name: Mapped[str] = mapped_column(String(40), nullable = True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable = False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default = True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"User id: {self.id}, email: {self.email})"
    