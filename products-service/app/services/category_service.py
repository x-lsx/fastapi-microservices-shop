from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import status, HTTPException

from sqlalchemy.exc import IntegrityError

from ..repositories.category_repository import CategoryRepository
from ..schemas.category import CategoryResponse, CategoryUpdate, CategoryCreate
from ..models.category import Category

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CategoryRepository(db)
        
    async def list(self) -> List[Category]:
        return await self.repo.get_all()

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        return await self.repo.get_by_id(category_id)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        return await self.repo.get_by_slug(slug)
    
    async def create(self, data: CategoryCreate) -> Category:
        existing = await self.repo.get_by_slug(data.slug)
        if existing:
            raise ValueError(f"Category with slug '{data.slug}' s")

        all_cats = await self.repo.get_all()
        if any(c.name == data.name for c in all_cats):
            raise ValueError(f"Category with name '{data.name}' already exists")

        try:
            return await self.repo.create(data)
        except IntegrityError as e:
            raise ValueError("Database integrity error when creating category") from e
        
    async def update(self, category_id: int, data: CategoryUpdate) -> Category:
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise ValueError("Category not found")

        dd = data.model_dump(exclude_unset=True)
        if "slug" in dd:
            other = await self.repo.get_by_slug(dd["slug"])
            if other and other.id != category_id:
                raise ValueError(f"Another category with slug '{dd['slug']}' already exists")

        if "name" in dd:
            all_cats = await self.repo.get_all()
            if any(c.name == dd["name"] and c.id != category_id for c in all_cats):
                raise ValueError(f"Another category with name '{dd['name']}' already exists")

        try:
            return await self.repo.update(category_id, dd)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("Database integrity error when updating category") from e

    async def delete(self, category_id: int) -> None:
        ok = await self.repo.delete(category_id)
        if not ok:
            raise ValueError("Category not found or could not be deleted")