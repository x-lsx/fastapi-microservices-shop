from typing import List, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, String, Boolean, Text, func, DateTime
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from datetime import datetime
from ..core.database import Base

if TYPE_CHECKING:
    from .product_size import ProductSize
    from .product_image import ProductImage


class Product(Base):
    __tablename__="products"
    
    id: Mapped[int] = mapped_column(Integer, autoincrement = True, primary_key = True, index = True)
    name: Mapped[str] = mapped_column(String(50), nullable = False, unique = True)
    price: Mapped[float] = mapped_column(Float, nullable = False)
    description: Mapped[str] = mapped_column(Text, nullable = True) 
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default = True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category: Mapped["Category"] = relationship("Category", back_populates = "products")
    # association to ProductSize so we can access quantity and size via Product.sizes
    sizes: Mapped[List["ProductSize"]] = relationship("ProductSize", back_populates="product")
    # images for product
    images: Mapped[List["ProductImage"]] = relationship("ProductImage", back_populates="product")