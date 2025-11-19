from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..repositories.size_repository import SizeRepository
from ..schemas.size import SizeCreate, SizeUpdate
from ..models.size import Size


class SizeService:
    def __init__(self, db: AsyncSession):
        self.repo = SizeRepository(db)

    async def list(self) -> List[Size]:
        return await self.repo.get_all()

    async def get(self, size_id: int) -> Optional[Size]:
        return await self.repo.get_by_id(size_id)

    async def get_by_value(self, value: str) -> Optional[Size]:
        return await self.repo.get_by_value(value)

    async def create(self, data: SizeCreate) -> Size:
        existing = await self.repo.get_by_value(data.value)
        if existing:
            raise ValueError(f"Size '{data.value}' already exists")
        try:
            return await self.repo.create(data)
        except IntegrityError as e:
            raise ValueError("Database integrity error when creating size") from e

    async def update(self, size_id: int, data: SizeUpdate) -> Size:
        size = await self.repo.get_by_id(size_id)
        if not size:
            raise ValueError("Size not found")

        dd = data.model_dump(exclude_unset=True)
        if "value" in dd:
            other = await self.repo.get_by_value(dd["value"])
            if other and other.id != size_id:
                raise ValueError(f"Another size with value '{dd['value']}' already exists")

        try:
            return await self.repo.update(size_id, dd)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("Database integrity error when updating size") from e

    async def delete(self, size_id: int) -> None:
        ok = await self.repo.delete(size_id)
        if not ok:
            raise ValueError("Size not found or could not be deleted")