from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.cart import CartRepository
from ..core.client import ProductClient
from ..models.cart import CartItem

class CartService:
    def __init__(self, db: AsyncSession, product_client: ProductClient):
        self.repo = CartRepository(db)
        self.client = product_client

    async def get_cart(self, user_id: int):
        cart = await self.repo.get_cart(user_id)
        if not cart:
            cart = await self.repo.create_cart(user_id)
        return cart

    async def add_item(self, user_id: int, product_id: int, size_id: int, quantity: int):
        # 1. Проверка наличия продукта и размера
        product_data = await self.client.validate_product_and_size(product_id, size_id, quantity)

        # 2. Получаем корзину
        cart = await self.get_cart(user_id)

        # 3. Проверка существующего товара
        existing_item = next(
            (i for i in cart.items if i.product_id == product_id and i.size_id == size_id), None
        )
        if existing_item:
            existing_item.quantity += quantity
            await self.repo.update_item(existing_item, existing_item.quantity)
        else:
            await self.repo.add_item(cart, product_id, size_id, quantity, product_data["product"]["price"])

        return await self.get_cart(user_id)

    async def remove_item(self, user_id: int, product_id: int, size_id: int):
        cart = await self.get_cart(user_id)
        item = next(
            (i for i in cart.items if i.product_id == product_id and i.size_id == size_id), None
        )
        if not item:
            raise HTTPException(status_code=404, detail="Item not found in cart")
        await self.repo.remove_item(item)
        return await self.get_cart(user_id)

    async def change_item_quantity(self, user_id: int, product_id: int, size_id: int, delta: int):

        if delta == 0:
            return await self.get_cart(user_id)

        cart = await self.get_cart(user_id)
        item = next(
            (i for i in cart.items if i.product_id == product_id and i.size_id == size_id), None
        )

        if not item:
            if delta > 0:

                product_data = await self.client.validate_product_and_size(product_id, size_id, delta)
                await self.repo.add_item(cart, product_id, size_id, delta, product_data["product"]["price"])
                return await self.get_cart(user_id)
            else:
                raise HTTPException(status_code=404, detail="Item not found in cart")

        new_qty = item.quantity + delta
        if new_qty <= 0:
            await self.repo.remove_item(item)
            return await self.get_cart(user_id)

        if delta > 0:
            await self.client.validate_product_and_size(product_id, size_id, new_qty)

        await self.repo.update_item(item, new_qty)
        return await self.get_cart(user_id)

    async def clear_cart(self, user_id: int):
        cart = await self.get_cart(user_id)
        for item in cart.items:
            await self.repo.remove_item(item)
        return cart
