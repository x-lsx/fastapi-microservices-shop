import httpx
from fastapi import HTTPException
from typing import Optional


class ProductClient:
    """Simple HTTP client for the products service.

    Keeps an AsyncClient instance to reuse connections (reduces latency).
    """

    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        # reuse client to avoid creating a new connection per request
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

        # data["sizes"] contains ProductSize objects with nested size
        size_item = next((s for s in data.get("sizes", []) if s.get("size", {}).get("id") == size_id), None)
        if not size_item:
            raise HTTPException(400, "Size not found for this product")

        if size_item.get("quantity", 0) < quantity:
            raise HTTPException(400, "Not enough stock")

        return {"product": data, "size": size_item}

    async def close(self):
        await self._client.aclose()
