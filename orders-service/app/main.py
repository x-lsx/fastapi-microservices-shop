from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.routes import orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # close external HTTP clients used by routes
    try:
        from app.routes import orders as orders_routes
        await orders_routes.product_client.close()
        await orders_routes.cart_client.close()
    except Exception:
        pass
    await close_db()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    lifespan=lifespan 
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)


@app.get("/")
def root():
    return {"message": "Orders service"}
