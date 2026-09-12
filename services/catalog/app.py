import json
from fastapi import FastAPI, Depends, HTTPException, Query
from prometheus_client import make_asgi_app
from redis.asyncio import Redis
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from services.catalog.db import get_db, init_db
from services.catalog.models import Product
from services.catalog.schemas import ProductCreate, ProductOut, StockUpdate
from shared.config import get_settings
from shared.dependencies import require_roles, current_user
from shared.logging import configure_logging
from shared.middleware import ObservabilityMiddleware

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Enterprise Catalog Service",
    version="1.0.0",
    description="Product catalog, stock and Redis caching.",
)
app.add_middleware(ObservabilityMiddleware, service_name="catalog")
app.mount("/metrics", make_asgi_app())
redis_client: Redis | None = None

@app.on_event("startup")
async def startup():
    global redis_client
    await init_db()
    try:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
    except Exception:
        redis_client = None

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "catalog", "cache": bool(redis_client)}

@app.get("/ready")
async def ready():
    return {"status": "ready", "service": "catalog"}

@app.get("/products", response_model=list[ProductOut])
async def list_products(
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"products:{q or '*'}:{limit}"
    if redis_client:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

    stmt = select(Product).limit(limit)
    if q:
        term = f"%{q}%"
        stmt = select(Product).where(
            or_(Product.name.ilike(term), Product.sku.ilike(term))
        ).limit(limit)

    result = await db.execute(stmt)
    products = result.scalars().all()
    payload = [ProductOut.model_validate(p).model_dump(mode="json") for p in products]

    if redis_client:
        await redis_client.set(cache_key, json.dumps(payload), ex=60)
    return payload

@app.post("/products", response_model=ProductOut, status_code=201)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    existing = await db.execute(select(Product).where(Product.sku == payload.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="SKU already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    if redis_client:
        await redis_client.delete("products:*:50")
    return product

@app.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.patch("/products/{product_id}/stock", response_model=ProductOut)
async def update_stock(
    product_id: int,
    payload: StockUpdate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.stock = payload.quantity
    await db.commit()
    await db.refresh(product)
    return product
