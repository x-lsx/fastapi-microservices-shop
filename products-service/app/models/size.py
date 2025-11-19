from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from ..core.database import Base

if TYPE_CHECKING:
    from .product_size import ProductSize


class Size(Base):
    __tablename__ = "sizes"
    id: Mapped[int] = mapped_column(Integer, autoincrement = True, primary_key = True, index = True)
    value: Mapped[str] = mapped_column(String(10), unique = True)
    
    
    # association to ProductSize so we can access quantity per product
    product_sizes: Mapped[List["ProductSize"]] = relationship("ProductSize", back_populates="size")