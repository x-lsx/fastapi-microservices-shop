from sqlalchemy import Float, ForeignKey, Integer, String, Boolean, Text, func, DateTime
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from datetime import datetime
from ..core.database import Base


class ProductSize(Base):
    __tablename__ = "product_sizes"
    
    id: Mapped[int] = mapped_column(Integer, autoincrement = True, primary_key = True, index = True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    size_id: Mapped[int] = mapped_column(ForeignKey("sizes.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    
    product: Mapped["Product"] = relationship("Product", back_populates="sizes")
    size: Mapped["Size"] = relationship("Size", back_populates="product_sizes")