import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from shared.logging import logger
from shared.metrics import REQUEST_COUNT, REQUEST_LATENCY

class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
            return response
        finally:
            elapsed = time.perf_counter() - start
            status = getattr(locals().get("response"), "status_code", 500)
            path = request.url.path
            REQUEST_COUNT.labels(
                self.service_name, request.method, path, str(status)
            ).inc()
            REQUEST_LATENCY.labels(
                self.service_name, request.method, path
            ).observe(elapsed)
            logger.info(
                "request",
                service=self.service_name,
                method=request.method,
                path=path,
                status=status,
                duration_ms=round(elapsed * 1000, 2),
            )
