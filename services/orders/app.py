from decimal import Decimal
import os
import httpx
from fastapi import FastAPI, Depends, HTTPException
from prometheus_client import make_asgi_app
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.orders.db import get_db, init_db
from services.orders.models import Order
from services.orders.schemas import OrderCreate, OrderOut
from shared.config import get_settings
from shared.dependencies import current_user
from shared.logging import configure_logging
from shared.middleware import ObservabilityMiddleware

settings = get_settings()
configure_logging(settings.log_level)
CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002")

app = FastAPI(
    title="Enterprise Orders Service",
    version="1.0.0",
    description="Order creation and order history.",
)
app.add_middleware(ObservabilityMiddleware, service_name="orders")
app.mount("/metrics", make_asgi_app())

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "orders"}

@app.get("/ready")
async def ready():
    return {"status": "ready", "service": "orders"}

@app.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(
    payload: OrderCreate,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{CATALOG_URL}/products/{payload.product_id}")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Product not found")
    product = response.json()
    if product["stock"] < payload.quantity:
        raise HTTPException(status_code=409, detail="Insufficient stock")

    unit_price = Decimal(str(product["price"]))
    total = unit_price * payload.quantity
    order = Order(
        user_id=int(user["sub"]),
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit_price=unit_price,
        total_amount=total,
        status="created",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

@app.get("/orders", response_model=list[OrderOut])
async def list_orders(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.user_id == int(user["sub"])).order_by(Order.id.desc())
    )
    return result.scalars().all()

@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == int(user["sub"]),
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
