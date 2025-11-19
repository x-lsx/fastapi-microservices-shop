from pydantic import BaseModel, ConfigDict


class ProductImageResponse(BaseModel):
    id: int
    file_name: str

    model_config = ConfigDict(from_attributes=True)


class ProductImageUploadResponse(BaseModel):
    id: int
    url: str

    model_config = ConfigDict(from_attributes=True)
