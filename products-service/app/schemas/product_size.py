
from pydantic import BaseModel, Field, ConfigDict
from .size import SizeResponse


class ProductSizeCreate(BaseModel):
    size_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


class ProductSizeResponse(BaseModel):
    quantity: int
    size: SizeResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductSizeUpdate(ProductSizeCreate):
    pass
