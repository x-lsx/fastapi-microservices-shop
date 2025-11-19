from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse
from ..services.product_service import ProductService
from ..core.dependencies import get_current_user
from ..core.database import get_db
from fastapi import UploadFile, File
from pathlib import Path
from fastapi import Depends
from app.repositories.product_image_repository import ProductImageRepository
from app.core.config import settings
from fastapi.concurrency import run_in_threadpool
from ..schemas.product_image import ProductImageUploadResponse
from ..schemas import product as _product_schemas
from ..schemas import product_size as _ps_schemas
from ..schemas.stock import StockChangeItem
from ..repositories.product_size_repository import ProductSizeRepository
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from fastapi import Body

router = APIRouter(prefix="/products", tags=["products"])

# --- Список всех продуктов ---
@router.get("/", response_model=List[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.list()

# --- Получение продукта по ID ---
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_by_id(product_id)

# --- Получение продуктов по slug категории ---
@router.get("/category/{slug}", response_model=List[ProductResponse])
async def get_products_by_category(slug: str, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_by_category_slug(slug)

# --- Создание продукта (только для суперюзеров) ---
@router.post("/create", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    service = ProductService(db)
    return await service.create(data)

# --- Обновление продукта (только для суперюзеров) ---
@router.put("/update/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    service = ProductService(db)
    return await service.update(product_id, data)

# --- Удаление продукта (только для суперюзеров) ---
@router.delete("/delete/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    service = ProductService(db)
    await service.delete(product_id)
    return {"detail": "Product deleted"}


@router.post("/update/{product_id}/images", response_model=List[ProductImageUploadResponse])
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Ensure product exists
    service = ProductService(db)
    product = await service.get_by_id(product_id)

    # prepare destination
    images_dir = Path(settings.images_dir) / "products" / str(product_id)
    images_dir.mkdir(parents=True, exist_ok=True)
    dest_path = images_dir / file.filename

    # save file in threadpool to avoid blocking
    with dest_path.open("wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            await run_in_threadpool(buffer.write, chunk)
    await file.close()

    # save record in db
    img_repo = ProductImageRepository(db)
    img = await img_repo.create(product_id=product_id, file_name=str(Path("images") / "products" / str(product_id) / file.filename))
    await db.commit()

    # return minimal info (file url)
    url = f"/static/{img.file_name}"
    return [{"id": img.id, "url": url}]


@router.post("/reserve", status_code=status.HTTP_200_OK)
async def reserve_stock(items: List[StockChangeItem] = Body(...), db: AsyncSession = Depends(get_db)):
    """Reserve stock for multiple items atomically."""
    repo = ProductSizeRepository(db)
    # normalize items to dicts
    payload = [{"product_id": i.size_id and i.size_id and i.__dict__.get('product_id') or i.__dict__.get('product_id', None),
                "size_id": i.size_id, "quantity": i.quantity} for i in items]
    # Above line keeps shape but in our ProductSizeCreate we only have size_id and quantity when used per-product.
    # We'll accept that callers pass product_id in each item dict as well.
    # Simpler: convert as dict
    payload = [i.model_dump() if hasattr(i, 'model_dump') else i for i in items]
    await repo.reserve_many(payload)
    return {"detail": "reserved"}


@router.post("/release", status_code=status.HTTP_200_OK)
async def release_stock(items: List[StockChangeItem] = Body(...), db: AsyncSession = Depends(get_db)):
    repo = ProductSizeRepository(db)
    payload = [i.model_dump() if hasattr(i, 'model_dump') else i for i in items]
    await repo.release_many(payload)
    return {"detail": "released"}
