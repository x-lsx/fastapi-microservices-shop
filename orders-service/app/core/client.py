import httpx
from fastapi import HTTPException


class ProductClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout)

    async def get_product(self, product_id: int) -> dict:
        url = f"{self.base_url}/products/{product_id}"
        try:
            resp = await self._client.get(url)
        except httpx.RequestError:
            raise HTTPException(500, "Product service unavailable")

        if resp.status_code == 404:
            raise HTTPException(404, "Product not found")
        if resp.status_code != 200:
            raise HTTPException(500, "Product service unavailable")

        return resp.json()

    async def validate_product_and_size(self, product_id: int, size_id: int, quantity: int):
        data = await self.get_product(product_id)
        size_item = next((s for s in data.get("sizes", []) if s.get("size", {}).get("id") == size_id), None)
        if not size_item:
            raise HTTPException(400, "Size not found for this product")

        if size_item.get("quantity", 0) < quantity:
            raise HTTPException(400, "Not enough stock")

        return {"product": data, "size": size_item}

    async def reserve_items(self, items: list):
        """Reserve multiple items on products-service. Items: list of {product_id,size_id,quantity}"""
        url = f"{self.base_url}/products/reserve"
        try:
            resp = await self._client.post(url, json=items)
        except httpx.RequestError:
            raise HTTPException(500, "Product service unavailable")

        if resp.status_code != 200:
            # bubble up product service message if present
            detail = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None
            raise HTTPException(status_code=resp.status_code, detail=detail or "Reserve failed")

    async def release_items(self, items: list):
        url = f"{self.base_url}/products/release"
        try:
            resp = await self._client.post(url, json=items)
        except httpx.RequestError:
            raise HTTPException(500, "Product service unavailable")

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Release failed")

    async def close(self):
        await self._client.aclose()


class CartClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout)

    async def get_cart(self, user_id: int) -> dict:
        url = f"{self.base_url}/cart/"
        headers = {"x-user-id": str(user_id)}
        try:
            resp = await self._client.get(url, headers=headers)
        except httpx.RequestError:
            raise HTTPException(500, "Cart service unavailable")

        if resp.status_code != 200:
            raise HTTPException(500, "Cart service error")

        return resp.json()

    async def clear_cart(self, user_id: int):
        url = f"{self.base_url}/cart/clear"
        headers = {"x-user-id": str(user_id)}
        try:
            resp = await self._client.delete(url, headers=headers)
        except httpx.RequestError:
            raise HTTPException(500, "Cart service unavailable")

        if resp.status_code not in (200, 204):
            raise HTTPException(500, "Cart clear failed")

    async def close(self):
        await self._client.aclose()
