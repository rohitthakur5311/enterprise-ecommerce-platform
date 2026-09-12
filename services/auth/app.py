from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from prometheus_client import make_asgi_app
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth.db import get_db, init_db
from services.auth.models import User
from services.auth.schemas import RegisterRequest, LoginRequest, UserOut, TokenResponse
from shared.config import get_settings
from shared.dependencies import current_user
from shared.logging import configure_logging
from shared.middleware import ObservabilityMiddleware
from shared.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token
)

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Enterprise Auth Service",
    version="1.0.0",
    description="Authentication, refresh tokens and RBAC.",
)
app.add_middleware(ObservabilityMiddleware, service_name="auth")
app.mount("/metrics", make_asgi_app())

@app.on_event("startup")
async def startup():
    await init_db()
    async for db in get_db():
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        if result.scalar_one_or_none() is None:
            db.add(User(
                email="admin@example.com",
                password_hash=hash_password("Admin123!"),
                role="admin",
            ))
            await db.commit()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth"}

@app.get("/ready")
async def ready():
    return {"status": "ready", "service": "auth"}

@app.post("/auth/register", response_model=UserOut, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@app.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role),
        refresh_token=create_refresh_token(str(user.id), user.role),
        expires_in=settings.access_token_minutes * 60,
    )

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return TokenResponse(
        access_token=create_access_token(payload["sub"], payload["role"]),
        refresh_token=create_refresh_token(payload["sub"], payload["role"]),
        expires_in=settings.access_token_minutes * 60,
    )

@app.get("/auth/me", response_model=UserOut)
async def me(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="User not found")
    return record
