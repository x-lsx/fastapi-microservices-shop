from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .category import CategoryResponse
from .product_size import ProductSizeCreate, ProductSizeResponse
from .product_image import ProductImageResponse

class ProductBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category_id: int = Field(..., gt=0)

class ProductCreate(ProductBase):
    sizes: Optional[List[ProductSizeCreate]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    sizes: Optional[List[ProductSizeCreate]] = None
    
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    category: CategoryResponse
    sizes: List[ProductSizeResponse] = []
    images: Optional[List[ProductImageResponse]] = []

    model_config = ConfigDict(from_attributes=True)

ProductResponse.model_rebuild()
