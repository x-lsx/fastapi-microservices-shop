from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repository import OrderRepository
from app.core.client import ProductClient, CartClient


class OrderService:
    def __init__(self, db: AsyncSession, product_client: ProductClient, cart_client: CartClient):
        self.db = db
        self.repo = OrderRepository(db)
        self.product_client = product_client
        self.cart_client = cart_client

    async def place_order(self, user_id: int):
        cart = await self.cart_client.get_cart(user_id)
        items = cart.get("items", [])
        if not items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        order_items: List[dict] = []
        total = 0.0

        reserve_payload = []
        for it in items:
            pid = it.get("product_id")
            sid = it.get("size_id")
            qty = it.get("quantity")
            reserve_payload.append({"product_id": pid, "size_id": sid, "quantity": qty})

        await self.product_client.reserve_items(reserve_payload)

        try:
            for it in items:
                pid = it.get("product_id")
                sid = it.get("size_id")
                qty = it.get("quantity")
                prod_data = await self.product_client.get_product(pid)
                price = prod_data.get("price", it.get("price", 0.0))
                order_items.append({"product_id": pid, "size_id": sid, "quantity": qty, "price": price})
                total += price * qty

            order = await self.repo.create_order(user_id=user_id, total_price=total, items=order_items)

            await self.cart_client.clear_cart(user_id)

            return order
        except Exception:
            try:
                await self.product_client.release_items(reserve_payload)
            except Exception:
                pass
            raise
