from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Response, status
import httpx
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

from config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(
    title="API Gateway",
    description="Gateway для всех микросервисов магазина",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
client = httpx.AsyncClient(timeout=10.0)


# ----------------------- JWT -----------------------

def create_access_token(user_id: int, username: str, is_superuser: bool, expires_delta=None):
    to_encode = {
        "id": user_id,
        "username": username,
        "is_superuser": is_superuser,
        "exp": datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        return None

    scheme, _, token = auth.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return None

    payload = decode_token(token)
    return {
        "id": payload["id"],
        "username": payload["username"],
        "is_superuser": payload["is_superuser"]
    }


async def proxy_request(request: Request, service_url: str, path: str):
    user = await get_current_user(request)

    # Копируем заголовки корректно
    headers = {k: v for k, v in request.headers.items()}
    headers.pop("host", None)

    # Добавляем user-info
    if user:
        headers["X-User-Id"] = str(user["id"])
        headers["X-User-Name"] = user["username"]
        headers["X-User-IsSuper"] = "1" if user["is_superuser"] else "0"

    body = await request.body()

    async with httpx.AsyncClient() as session:
        resp = await session.request(
            method=request.method,
            url=f"{service_url}{path}",
            headers=headers,
            params=request.query_params,
            content=body
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers)
    )

# ----------------------- AUTH -----------------------

@app.post("/auth/login")
async def login(request: Request):
    data = await request.json()

    # проброс на user-service
    resp = await client.post(f"{settings.USER_SERVICE_URL}/auth/login", json=data)

    user = resp.json()

    token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        is_superuser=user["is_superuser"]
    )

    return {"access_token": token, "token_type": "bearer"}

@app.api_route("/users/register", methods=["POST"])
async def proxy_user_register(request: Request):
    """Проксируем регистрацию"""
    return await proxy_request(
        request,
        settings.USER_SERVICE_URL,
        "/users/register"
    )


@app.api_route("/users/me", methods=["GET"])
async def proxy_user_me(request: Request):
    """Проксируем получение текущего пользователя"""

    return await proxy_request(
        request,
        settings.USER_SERVICE_URL,
        "/users/me"
    )


# ----------------------- PROXY ROUTES -----------------------

@app.api_route("/products/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_products(full_path: str, request: Request):
    return await proxy_request(
        request,
        settings.PRODUCT_SERVICE_URL,
        f"/products/{full_path}"
    )


@app.api_route("/categories/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_categories(full_path: str, request: Request):
    return await proxy_request(
        request,
        settings.PRODUCT_SERVICE_URL,
        f"/categories/{full_path}"
    )


@app.api_route("/sizes/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_sizes(full_path: str, request: Request):
    return await proxy_request(
        request,
        settings.PRODUCT_SERVICE_URL,
        f"/sizes/{full_path}"
    )


@app.api_route("/cart/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_cart(full_path: str, request: Request):
    return await proxy_request(
        request,
        settings.CART_SERVICE_URL,
        f"/cart/{full_path}"
    )


@app.api_route("/orders/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_orders(full_path: str, request: Request):
    return await proxy_request(
        request,
        settings.ORDER_SERVICE_URL,
        f"/orders/{full_path}"
    )
