from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from app.models.product_size import ProductSize
from app.schemas.product_size import ProductSizeCreate, ProductSizeUpdate


class ProductSizeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_by_product(self, product_id: int) -> List[ProductSize]:
        result = await self.db.execute(
            select(ProductSize).where(ProductSize.product_id == product_id)
        )
        return result.scalars().all()

    async def get_by_id(self, ps_id: int) -> Optional[ProductSize]:
        result = await self.db.execute(
            select(ProductSize).where(ProductSize.id == ps_id)
        )
        return result.scalar_one_or_none()
    

    async def create(self, product_id: int, data: ProductSizeCreate) -> ProductSize:
        new_ps = ProductSize(
            product_id=product_id,
            size_id=data.size_id,
            quantity=data.quantity,
        )
        self.db.add(new_ps)
        await self.db.flush()
        await self.db.refresh(new_ps)
        return new_ps

    async def update(self, ps_id: int, data: ProductSizeUpdate) -> Optional[ProductSize]:
        ps = await self.get_by_id(ps_id)
        if not ps:
            return None
        
        update_payload = data.model_dump(exclude_unset=True)
        for field, value in update_payload.items():
            setattr(ps, field, value)

        await self.db.flush()
        await self.db.refresh(ps)
        return ps

    async def delete(self, ps_id: int) -> bool:
        ps = await self.get_by_id(ps_id)
        if not ps:
            return False

        await self.db.delete(ps)
        await self.db.flush()
        return True

    async def delete_by_product(self, product_id: int):
        await self.db.execute(delete(ProductSize).where(ProductSize.product_id == product_id))

    async def reserve_many(self, items: List[dict]) -> None:
        """Atomically reserve (decrement) quantity for given items.

        items: list of {'product_id': int, 'size_id': int, 'quantity': int}
        Raises HTTPException(400) if any item lacks stock.
        """
        # perform checks and updates within a transaction
        async with self.db.begin():
            for it in items:
                product_id = it["product_id"]
                size_id = it["size_id"]
                qty = it["quantity"]

                result = await self.db.execute(
                    select(ProductSize).where(
                        ProductSize.product_id == product_id,
                        ProductSize.size_id == size_id
                    )
                )
                ps = result.scalar_one_or_none()
                if not ps:
                    from fastapi import HTTPException
                    raise HTTPException(status_code=400, detail=f"Size {size_id} for product {product_id} not found")
                if ps.quantity < qty:
                    from fastapi import HTTPException
                    raise HTTPException(status_code=400, detail=f"Not enough stock for product {product_id} size {size_id}")
                ps.quantity = ps.quantity - qty
                await self.db.flush()

    async def release_many(self, items: List[dict]) -> None:
        """Release (increment) quantity for given items."""
        async with self.db.begin():
            for it in items:
                product_id = it["product_id"]
                size_id = it["size_id"]
                qty = it["quantity"]

                result = await self.db.execute(
                    select(ProductSize).where(
                        ProductSize.product_id == product_id,
                        ProductSize.size_id == size_id
                    )
                )
                ps = result.scalar_one_or_none()
                if not ps:
                    continue
                ps.quantity = ps.quantity + qty
                await self.db.flush()