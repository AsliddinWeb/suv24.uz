from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=32)
    password: str = Field(min_length=1, max_length=128)
    company_slug: str | None = Field(default=None, max_length=64)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    access_ttl_seconds: int
    refresh_ttl_seconds: int


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class LoginResponse(TokenPair):
    user: UserOut
