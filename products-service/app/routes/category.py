from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..core.dependencies import get_current_user
from ..core.database import get_db
from ..services.category_service import CategoryService
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return await service.list()

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/create", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden asd")
    service = CategoryService(db)
    return await service.create(data)


@router.put("/update/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, data: CategoryUpdate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    service = CategoryService(db)
    return await service.update(category_id, data)


@router.delete("/delete/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    service = CategoryService(db)
    await service.delete(category_id)
    return {"detail": "Category deleted"}
