from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..core.dependencies import get_current_user
from ..core.database import get_db
from ..services.size_service import SizeService
from ..schemas.size import SizeCreate, SizeUpdate, SizeResponse

router = APIRouter(prefix="/sizes", tags=["sizes"])

@router.get("/", response_model=List[SizeResponse])
async def list_sizes(db: AsyncSession = Depends(get_db)):
    service = SizeService(db)
    return await service.list()


@router.post("/create", response_model=SizeResponse, status_code=status.HTTP_201_CREATED)
async def create_size(
    data: SizeCreate,
    admin: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = SizeService(db)
    return await service.create(data)


@router.put("/update/{size_id}", response_model=SizeResponse)
async def update_size(
    size_id: int,
    data: SizeUpdate,
    admin: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = SizeService(db)
    return await service.update(size_id, data)


@router.delete("/delete/{size_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_size(
    size_id: int,
    admin: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = SizeService(db)
    await service.delete(size_id)
    return {"detail": "Size deleted"}
