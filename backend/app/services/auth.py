from datetime import timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository
from app.schemas.auth import TokenPair


REFRESH_KEY_PREFIX = "auth:refresh:"


def _refresh_key(jti: str) -> str:
    return f"{REFRESH_KEY_PREFIX}{jti}"


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis) -> None:
        self.db = db
        self.redis = redis
        self.users = UserRepository(db)
        self.companies = CompanyRepository(db)

    async def authenticate(
        self,
        phone: str,
        password: str,
        company_slug: str | None,
    ) -> User:
        slug = company_slug or settings.DEFAULT_COMPANY_SLUG
        company = await self.companies.get_by_slug(slug)
        if company is None or not company.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        user = await self.users.get_by_phone(company.id, phone)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return user

    async def issue_tokens(self, user: User) -> TokenPair:
        access, _ = create_access_token(
            user_id=user.id,
            role=user.role.value,
            company_id=user.company_id,
        )
        refresh, r_claims = create_refresh_token(
            user_id=user.id,
            company_id=user.company_id,
        )
        ttl = timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
        await self.redis.set(
            _refresh_key(r_claims["jti"]),
            str(user.id),
            ex=int(ttl.total_seconds()),
        )
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            access_ttl_seconds=settings.JWT_ACCESS_TTL_MINUTES * 60,
            refresh_ttl_seconds=int(ttl.total_seconds()),
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, expected_type=TokenType.REFRESH)
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=401, detail="Refresh token expired") from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

        jti = payload["jti"]
        stored_user_id = await self.redis.get(_refresh_key(jti))
        if stored_user_id is None:
            raise HTTPException(status_code=401, detail="Refresh token revoked")

        user = await self.users.get_by_id(UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="User inactive")

        await self.redis.delete(_refresh_key(jti))
        return await self.issue_tokens(user)

    async def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        try:
            payload = decode_token(refresh_token, expected_type=TokenType.REFRESH)
        except jwt.InvalidTokenError:
            return
        await self.redis.delete(_refresh_key(payload["jti"]))
