from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _build_claims(
    subject: str,
    token_type: TokenType,
    ttl: timedelta,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    claims: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "jti": str(uuid4()),
        "type": token_type.value,
    }
    if extra:
        claims.update(extra)
    return claims


def create_access_token(
    user_id: UUID,
    role: str,
    company_id: UUID | None,
    extra: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    claims = _build_claims(
        subject=str(user_id),
        token_type=TokenType.ACCESS,
        ttl=timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES),
        extra={
            "role": role,
            "company_id": str(company_id) if company_id else None,
            **(extra or {}),
        },
    )
    token = jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, claims


def create_refresh_token(
    user_id: UUID,
    company_id: UUID | None,
) -> tuple[str, dict[str, Any]]:
    claims = _build_claims(
        subject=str(user_id),
        token_type=TokenType.REFRESH,
        ttl=timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
        extra={"company_id": str(company_id) if company_id else None},
    )
    token = jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, claims


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "iat", "sub", "jti", "type"]},
    )
    if expected_type and payload.get("type") != expected_type.value:
        raise jwt.InvalidTokenError(f"expected {expected_type.value} token")
    return payload
