
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.size_repository import SizeRepository
from app.repositories.product_size_repository import ProductSizeRepository

from app.schemas.product import ProductCreate,ProductUpdate
from app.schemas.product_size import ProductSizeCreate
from ..models.product import Product

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)
        self.size_repository = SizeRepository(db)
        self.ps_repo = ProductSizeRepository(db)

    async def list(self):
        return await self.product_repository.get_all()

    async def get_by_id(self, product_id: int):
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def get_by_category_slug(self, slug: str):
        category = await self.category_repository.get_by_slug(slug)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return await self.product_repository.get_by_category_slug(category.slug)

    async def create(self, data: ProductCreate) -> Product:
        # проверяем категорию
        category = await self.category_repository.get_by_id(data.category_id)
        if not category:
            raise HTTPException(status_code=400, detail=f"Category {data.category_id} does not exist")
        product = await self.product_repository.create(data)
        await self.db.commit()
        # reload product via repository to ensure related fields are eagerly loaded
        return await self.product_repository.get_by_id(product.id)
    
    async def update(self, product_id: int, data: ProductUpdate) -> Product:
        # Проверка категории, если обновляется
        if data.category_id:
            category = await self.category_repository.get_by_id(data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category {data.category_id} does not exist"
                )

        updated = await self.product_repository.update(product_id, data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Коммит изменений
        await self.db.commit()
        # reload via repository to ensure relationships (category, sizes) are loaded
        return await self.product_repository.get_by_id(product_id)

    async def delete(self, product_id: int):
        deleted = await self.product_repository.delete(product_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Коммит удаления
        await self.db.commit()
        return {"detail": "Product deleted"}
    # async def create(self, data: ProductCreate):
    #     """
    #     Создаёт продукт + связывает категорию + размеры.
    #     Всё происходит в одной транзакции.
    #     """

    #     async with self.db.begin():
    #         # --- 1. Проверка категории ---
    #         category = await self.category_repository.get_by_id(data.category_id)
    #         if not category:
    #             raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"Category {data.category_id} does not exist")

    #         # --- 2. Создание продукта ---
    #         product = Product(
    #             name=data.name,
    #             price=data.price,
    #             description=data.description,
    #             category_id=data.category_id,
    #         )
    #         self.db.add(product)
    #         await self.db.flush() 

    #         # --- 3. Создание ProductSize ---
    #         for size_item in data.sizes:
    #             size = await self.size_repository.get_by_id(size_item.size_id)
    #             if not size:
    #                 raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"Size {size_item.size_id} does not exist")

    #             await self.ps_repo.create_raw(
    #                 product_id=product.id,
    #                 size_id=size_item.size_id,
    #                 quantity=size_item.quantity,
    #             )

    #     # --- 4. Возвращаем продукт вместе с размерами ---
    #     return await self.product_repository.get_by_id(product.id)

    # async def update(self, product_id: int, data: ProductUpdate):
    #     """
    #     Обновляет:
    #     • name
    #     • price
    #     • category
    #     • sizes (полная перезапись)
    #     """

    #     async with self.db.begin():
    #         product = await self.product_repository.get_by_id(product_id)
    #         if not product:
    #             raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = "Product not found")

    #         update_payload = data.model_dump(exclude_unset=True)

    #         # --- 1. Проверка категории ---
    #         if "category_id" in update_payload:
    #             cat_id = update_payload["category_id"]
    #             exists = await self.category_repository.get_by_id(cat_id)
    #             if not exists:
    #                 raise HTTPException(400, f"Category {cat_id} does not exist")

    #         # --- 2. Обновление полей продукта ---
    #         await self.product_repository.update(product_id, update_payload)

    #         # --- 3. Обновление размеров ---
    #         if data.sizes is not None:
    #             # удаляем старые размеры
    #             await self.ps_repo.delete_by_product(product_id)

    #             # добавляем новые
    #             for size_item in data.sizes:
    #                 size = await self.size_repository.get_by_id(size_item.size_id)
    #                 if not size:
    #                     raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail =  f"Size {size_item.size_id} does not exist")

    #                 await self.ps_repo.create_raw(
    #                     product_id=product_id,
    #                     size_id=size_item.size_id,
    #                     quantity=size_item.quantity,
    #                 )

    #     # новое состояние
    #     return await self.product_repository.get_by_id(product_id)

    # async def delete(self, product_id: int):
    #     async with self.db.begin():
    #         exists = await self.product_repository.get_by_id(product_id)
    #         if not exists:
    #             raise HTTPException(404, "Product not found")

    #         # сначала удаляем размеры
    #         await self.ps_repo.delete_by_product(product_id)

    #         # потом сам продукт
    #         await self.product_repository.delete(product_id)

    #     return True
