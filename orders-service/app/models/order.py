from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, ForeignKey, DateTime, String, func
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="created")
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")
    

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer)
    size_id: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    
    order: Mapped["Order"] = relationship("Order", back_populates="items")