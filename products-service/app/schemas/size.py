from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class SizeBase(BaseModel):
    value: str = Field(..., max_length = 10)
    
class SizeCreate(SizeBase):
    pass

class SizeUpdate(BaseModel):
    value: Optional[str] = Field(None, max_length = 10)
    
class SizeResponse(SizeBase):
    id: int = Field(..., gt = 0)
    
    model_config = ConfigDict(from_attributes=True)