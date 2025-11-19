from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, user_id: int, total_price: float, items: List[dict]) -> Order:
        order = Order(user_id=user_id, total_price=total_price)
        self.db.add(order)
        await self.db.flush()

        for it in items:
            oi = OrderItem(
                order_id=order.id,
                product_id=it["product_id"],
                size_id=it["size_id"],
                quantity=it["quantity"],
                price=it["price"],
            )
            self.db.add(oi)

        await self.db.commit()
        # ensure related items are eagerly loaded before returning
        return await self.get_by_id(order.id)

    async def get_by_id(self, order_id: int) -> Order:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int):
        result = await self.db.execute(
            select(Order).where(Order.user_id == user_id).options(selectinload(Order.items))
        )
        return result.scalars().all()
