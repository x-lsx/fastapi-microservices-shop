from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.product_image import ProductImage


class ProductImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product_id: int, file_name: str) -> ProductImage:
        img = ProductImage(product_id=product_id, file_name=file_name)
        self.db.add(img)
        await self.db.flush()
        await self.db.refresh(img)
        return img

    async def get_by_product(self, product_id: int) -> List[ProductImage]:
        result = await self.db.execute(select(ProductImage).where(ProductImage.product_id == product_id))
        return result.scalars().all()
