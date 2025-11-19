from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List

from ..models.category import Category
from ..models.product import Product
from ..models.product_size import ProductSize
from ..models.product_image import ProductImage
from ..schemas.product import ProductCreate, ProductUpdate
from fastapi import HTTPException, status
from sqlalchemy import select

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.category),
                selectinload(Product.sizes).selectinload(ProductSize.size),
                selectinload(Product.images)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_category_slug(self, slug: str) -> List[Product]:
        result = await self.db.execute(
            select(Product)
            .join(Product.category)
            .where(Category.slug == slug)
            .options(
                selectinload(Product.category),
                selectinload(Product.sizes).selectinload(ProductSize.size),
                selectinload(Product.images)
            )
        )
        return result.scalars().all()
    
    async def get_all(self) -> List[Product]:
        result = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.sizes).selectinload(ProductSize.size),
                selectinload(Product.images)
            )
        )
        return result.scalars().all()

    async def create(self, data: ProductCreate) -> Product:
        """Создание продукта и размеров в одной транзакции"""
        # Проверяем, есть ли продукт с таким именем, чтобы избежать UNIQUE constraint error
        existing = await self.db.execute(select(Product).where(Product.name == data.name))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product with this name already exists")

        product = Product(
            name=data.name,
            price=data.price,
            description=data.description,
            category_id=data.category_id,
        )
        self.db.add(product)
        await self.db.flush()  # чтобы получить product.id

        if data.sizes:
            for size in data.sizes:
                self.db.add(
                    ProductSize(
                        product_id=product.id,
                        size_id=size.size_id,
                        quantity=size.quantity
                    )
                )
            await self.db.flush()

        return await self.get_by_id(product.id)

    async def update(self, product_id: int, data: ProductUpdate) -> Optional[Product]:
        """Обновление продукта и размеров в одной транзакции"""
        product = await self.db.get(Product, product_id)
        if not product:
            return None


        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "sizes":
                setattr(product, field, value)

        if "sizes" in update_data and update_data["sizes"] is not None:
            # удаляем старые размеры
            await self.db.execute(delete(ProductSize).where(ProductSize.product_id == product_id))
            # добавляем новые
            for size_item in update_data["sizes"]:
                self.db.add(
                    ProductSize(
                        product_id=product_id,
                        size_id=size_item.size_id,
                        quantity=size_item.quantity
                    )
                )
            await self.db.flush()

        return await self.get_by_id(product_id)

    async def delete(self, product_id: int) -> bool:
        product = await self.db.get(Product, product_id)
        if not product:
            return False
        await self.db.execute(
            delete(ProductSize).where(ProductSize.product_id == product_id)
        )
        await self.db.delete(product)
        await self.db.flush()
        return True