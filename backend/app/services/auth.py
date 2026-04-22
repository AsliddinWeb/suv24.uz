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
from sqlalchemy import select

from app.models.user import User, UserRole
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
        # Platform owner is not scoped to a company; look them up by phone alone.
        owner = await self._get_platform_owner_by_phone(phone)
        if owner is not None:
            if not owner.is_active or not verify_password(password, owner.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
            return owner

        # If slug is provided, scope to that company.
        if company_slug:
            company = await self.companies.get_by_slug(company_slug)
            if company is None or not company.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
            user = await self.users.get_by_phone(company.id, phone)
            candidates = [user] if user is not None else []
        else:
            # No slug: search across all active companies by phone.
            candidates = await self._find_active_users_by_phone(phone)

        if not candidates:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if len(candidates) > 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Bu telefon bir nechta kompaniyaga tegishli. "
                    "Kompaniya slug'ini kiriting."
                ),
            )

        user = candidates[0]
        if not user.is_active or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return user

    async def _get_platform_owner_by_phone(self, phone: str) -> User | None:
        stmt = select(User).where(
            User.phone == phone,
            User.role == UserRole.PLATFORM_OWNER,
            User.deleted_at.is_(None),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def _find_active_users_by_phone(self, phone: str) -> list[User]:
        from app.models.company import Company

        stmt = (
            select(User)
            .join(Company, Company.id == User.company_id)
            .where(
                User.phone == phone,
                User.deleted_at.is_(None),
                User.role != UserRole.PLATFORM_OWNER,
                User.is_active.is_(True),
                Company.is_active.is_(True),
                Company.deleted_at.is_(None),
            )
        )
        return list((await self.db.execute(stmt)).scalars().all())

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
