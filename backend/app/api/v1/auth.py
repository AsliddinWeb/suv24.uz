from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.deps import CurrentUser, DbDep, RedisDep
from app.core.rate_limit import limiter
from app.core.security import hash_password, verify_password
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, TokenPair
from app.schemas.common import OkResponse
from app.schemas.user import UserOut
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "wdms_refresh"


def _set_refresh_cookie(response: Response, token: str, max_age: int) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.APP_ENV != "development",
        samesite="lax",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/api/v1/auth")


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: DbDep,
    redis: RedisDep,
) -> LoginResponse:
    service = AuthService(db, redis)
    user = await service.authenticate(
        phone=payload.phone,
        password=payload.password,
        company_slug=payload.company_slug,
    )
    tokens = await service.issue_tokens(user)
    await db.commit()
    _set_refresh_cookie(response, tokens.refresh_token, tokens.refresh_ttl_seconds)
    return LoginResponse(**tokens.model_dump(), user=UserOut.model_validate(user))


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    response: Response,
    db: DbDep,
    redis: RedisDep,
) -> TokenPair:
    refresh_token = body.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    service = AuthService(db, redis)
    tokens = await service.refresh(refresh_token)
    _set_refresh_cookie(response, tokens.refresh_token, tokens.refresh_ttl_seconds)
    return tokens


@router.post("/logout", response_model=OkResponse)
async def logout(
    request: Request,
    body: RefreshRequest,
    response: Response,
    db: DbDep,
    redis: RedisDep,
) -> OkResponse:
    refresh_token = body.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    service = AuthService(db, redis)
    await service.logout(refresh_token)
    _clear_refresh_cookie(response)
    return OkResponse()


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


class UpdateMeRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=7, max_length=32)


@router.patch("/me", response_model=UserOut)
async def update_me(
    payload: UpdateMeRequest,
    user: CurrentUser,
    db: DbDep,
) -> UserOut:
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(user, field, value)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone already registered",
        ) from exc
    await db.refresh(user)
    return UserOut.model_validate(user)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


@router.post("/me/password", response_model=OkResponse)
async def change_my_password(
    payload: ChangePasswordRequest,
    user: CurrentUser,
    db: DbDep,
) -> OkResponse:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joriy parol noto'g'ri",
        )
    user.password_hash = hash_password(payload.new_password)
    await db.commit()
    return OkResponse()
