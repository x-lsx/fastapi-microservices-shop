from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.order_service import OrderService
from app.schemas.order import OrderResponse
from app.core.client import ProductClient, CartClient

router = APIRouter(prefix="/orders", tags=["orders"])

# clients - point to product and cart services
product_client = ProductClient(base_url="http://localhost:8002")
cart_client = CartClient(base_url="http://localhost:8003")


async def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db=db, product_client=product_client, cart_client=cart_client)


@router.post("/create", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(request: Request, service: OrderService = Depends(get_order_service)):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID missing in headers")

    order = await service.place_order(int(user_id))
    return order


@router.get("/", response_model=List[OrderResponse])
async def list_orders(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID missing in headers")

    from app.repositories.order_repository import OrderRepository
    repo = OrderRepository(db)
    orders = await repo.list_by_user(int(user_id))
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID missing in headers")

    from app.repositories.order_repository import OrderRepository
    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id)
    if not order or order.user_id != int(user_id):
        raise HTTPException(status_code=404, detail="Order not found")
    return order
