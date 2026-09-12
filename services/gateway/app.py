import os
from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import make_asgi_app
import httpx
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from shared.config import get_settings
from shared.logging import configure_logging
from shared.middleware import ObservabilityMiddleware

settings = get_settings()
configure_logging(settings.log_level)

AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002")
ORDERS_URL = os.getenv("ORDERS_SERVICE_URL", "http://localhost:8003")

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])

app = FastAPI(
    title="Enterprise E-Commerce API Gateway",
    version="1.0.0",
    description="Public entry point for the enterprise microservices platform.",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: Response("Rate limit exceeded", status_code=429))
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(ObservabilityMiddleware, service_name="gateway")
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}

@app.get("/ready")
async def ready():
    return {"status": "ready", "service": "gateway"}

async def proxy(request: Request, target: str, path: str):
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.request(
            request.method,
            f"{target}{path}",
            content=body,
            headers=headers,
            params=request.query_params,
        )
    excluded = {"content-encoding", "transfer-encoding", "connection"}
    response_headers = {k: v for k, v in response.headers.items() if k.lower() not in excluded}
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
        media_type=response.headers.get("content-type"),
    )

@app.api_route("/api/v1/auth/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def auth_proxy(request: Request, path: str):
    return await proxy(request, AUTH_URL, f"/auth/{path}")

@app.api_route("/api/v1/products{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def catalog_proxy(request: Request, path: str = ""):
    return await proxy(request, CATALOG_URL, f"/products{path}")

@app.api_route("/api/v1/orders{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def orders_proxy(request: Request, path: str = ""):
    return await proxy(request, ORDERS_URL, f"/orders{path}")
