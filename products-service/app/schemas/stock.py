from pydantic import BaseModel, Field
from typing import List


class StockChangeItem(BaseModel):
    product_id: int = Field(..., gt=0)
    size_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class StockChangeRequest(BaseModel):
    items: List[StockChangeItem]
