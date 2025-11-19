from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.cart import CartService
from ..schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse, CartItemChange
from ..core.client import ProductClient

router = APIRouter(prefix="/cart", tags=["Cart"])

product_client = ProductClient(base_url="http://localhost:8002")

async def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    return CartService(db=db, product_client=product_client)

# --- Получить корзину ---
@router.get("/", response_model = CartResponse)
async def get_cart(request: Request, service: CartService = Depends(get_cart_service)):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(401, "User ID missing in headers")
    return await service.get_cart(int(user_id))

# --- Добавить товар в корзину ---
@router.post("/add", response_model= CartResponse)
async def add_item(request: Request, data: CartItemCreate,
    service: CartService = Depends(get_cart_service)):
    
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(401, "User ID missing in headers")
    return await service.add_item(int(user_id), data.product_id, data.size_id, data.quantity)


@router.patch("/item", response_model=CartResponse)
async def patch_item(request: Request, data: CartItemChange,
                     service: CartService = Depends(get_cart_service)):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(401, "User ID missing in headers")
    # delta positive -> increase; negative -> decrease
    return await service.change_item_quantity(int(user_id), data.product_id, data.size_id, data.delta)

# --- Удалить товар из корзины ---
@router.delete("/remove", response_model= CartResponse)
async def remove_item(request: Request, data: CartItemCreate,
    service: CartService = Depends(get_cart_service)):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(401, "User ID missing in headers")
    return await service.remove_item(int(user_id), data.product_id, data.size_id)

# --- Очистить корзину ---
@router.delete("/clear", response_model= CartResponse)
async def clear_cart(request: Request, service: CartService = Depends(get_cart_service)):
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(401, "User ID missing in headers")
    return await service.clear_cart(int(user_id))
