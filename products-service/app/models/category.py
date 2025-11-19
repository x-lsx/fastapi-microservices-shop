from typing import List
from sqlalchemy import Integer, String
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from ..core.database import Base


class Category(Base):
    __tablename__="categories"
    id: Mapped[int] = mapped_column(Integer, autoincrement = True, primary_key = True, index = True)
    name: Mapped[str] = mapped_column(String(30), unique = True)
    slug: Mapped[str] = mapped_column(String(50), unique = True)
    
    products: Mapped[List["Product"]] = relationship("Product", back_populates = "category")