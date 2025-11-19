from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from ..models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- CART ---
    async def get_cart(self, user_id: int) -> Optional[Cart]:
        result = await self.db.execute(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_cart(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart

    async def delete_cart(self, cart: Cart):
        await self.db.delete(cart)
        await self.db.commit()

    # --- CART ITEMS ---
    async def add_item(self, cart: Cart, product_id: int, size_id: int, quantity: int, price: float):
        from ..models.cart import CartItem
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            size_id=size_id,
            quantity=quantity,
            price=price
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update_item(self, item: CartItem, quantity: int):
        item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def remove_item(self, item: CartItem):
        await self.db.delete(item)
        await self.db.commit()
