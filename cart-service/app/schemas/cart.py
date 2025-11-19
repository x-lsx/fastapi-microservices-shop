from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    size_id: int
    quantity: int
    
class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None


class CartItemChange(BaseModel):
    product_id: int
    size_id: int
    # positive = increase, negative = decrease
    delta: int

    model_config = ConfigDict(from_attributes=True)
    

class CartItemResponse(CartItemBase):
    price: float
    total_price: float
    
    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    total_quantity: int
    total_price: float

    model_config = ConfigDict(from_attributes=True)