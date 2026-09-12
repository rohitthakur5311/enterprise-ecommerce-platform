from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt

from shared.config import get_settings

settings = get_settings()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False

def create_token(subject: str, role: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def create_access_token(subject: str, role: str) -> str:
    return create_token(
        subject, role, "access",
        timedelta(minutes=settings.access_token_minutes)
    )

def create_refresh_token(subject: str, role: str) -> str:
    return create_token(
        subject, role, "refresh",
        timedelta(days=settings.refresh_token_days)
    )

def decode_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != expected_type or not payload.get("sub"):
            raise JWTError("Invalid token type")
        return payload
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
