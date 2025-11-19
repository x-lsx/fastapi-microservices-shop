from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class CategoryBase(BaseModel):
    name: str = Field(..., max_length = 30)
    slug: str
    
class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length = 30)
    
class CategoryResponse(CategoryBase):
    id: int = Field(..., gt = 0)

    model_config = ConfigDict(from_attributes=True)