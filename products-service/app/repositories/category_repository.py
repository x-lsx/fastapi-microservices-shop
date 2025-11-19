from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate

class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self) -> List[Category]:
        result = await self.db.execute(select(Category))
        return result.scalars().all()
        
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()
    
    async def create(self, category_data: CategoryCreate) -> Category:
        new_category = Category(**category_data.model_dump())
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)
        return new_category
    
    async def update(self, category_id: int, category_data: CategoryUpdate) -> Category:
        category = await self.get_by_id(category_id)
        if category:
            for field, value in category_data.items():
                setattr(category, field, value)
            await self.db.commit()
            await self.db.refresh(category)
        return category
        
    async def delete(self, category_id: int) -> bool:
        category = await self.get_by_id(category_id)
        if category:
            await self.db.delete(category)
            await self.db.commit()
            return True
        return False