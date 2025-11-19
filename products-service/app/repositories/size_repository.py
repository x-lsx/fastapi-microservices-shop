from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from ..models.size import Size
from ..schemas.size import SizeCreate, SizeUpdate

class SizeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Size]:
        result = await self.db.execute(select(Size))
        return result.scalars().all()
      
    async def get_by_id(self, size_id: int) -> Optional[Size]:
        result = await self.db.execute(select(Size).where(Size.id == size_id))
        return result.scalar_one_or_none()
    
    async def get_by_value(self, value: str) -> Optional[Size]:
        result = await self.db.execute(select(Size).where(Size.value == value))
        return result.scalar_one_or_none()
    
    async def create(self, size_data: SizeCreate) -> Size:
        new_size = Size(**size_data.model_dump())
        self.db.add(new_size)
        await self.db.commit()
        await self.db.refresh(new_size)
        return new_size
    
    async def update(self, size_id: int, size_data: dict) -> Optional[Size]:
        size = await self.get_by_id(size_id)
        if size:
            for field, value in size_data.items():
                setattr(size, field, value)
            await self.db.commit()
            await self.db.refresh(size)
        return size


    async def delete(self, size_id: int) -> bool:
        size = await self.get_by_id(size_id)
        if size:
            await self.db.delete(size)
            await self.db.commit()
            return True
        return False