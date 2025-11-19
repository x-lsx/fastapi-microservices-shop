from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    size_id: int
    quantity: int
    price: float

class OrderItemResponse(OrderItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)    

class OrderBase(BaseModel):
    user_id: int
    total_price: float
    status: Optional[str] = "created"
    
class OrderResponse(OrderBase):
    id: int
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)    