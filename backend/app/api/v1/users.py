from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.deps import DbDep, require_roles
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.common import OkResponse
from app.schemas.user import PasswordResetRequest, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

AdminUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
]


@router.get("", response_model=list[UserOut])
async def list_users(user: AdminUser, db: DbDep) -> list[UserOut]:
    stmt = (
        select(User)
        .where(User.company_id == user.company_id, User.deleted_at.is_(None))
        .order_by(User.created_at.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [UserOut.model_validate(u) for u in rows]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    user: AdminUser,
    db: DbDep,
) -> UserOut:
    if payload.role == UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Haydovchi yaratish uchun Haydovchilar sahifasidan foydalaning",
        )
    if payload.role == UserRole.PLATFORM_OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform owner bu sahifadan yaratilmaydi",
        )
    repo = UserRepository(db)
    try:
        created = await repo.create(
            User(
                company_id=user.company_id,
                phone=payload.phone,
                password_hash=hash_password(payload.password),
                full_name=payload.full_name,
                role=payload.role,
                is_active=True,
            )
        )
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone already registered in this company",
        ) from exc
    return UserOut.model_validate(created)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    user: AdminUser,
    db: DbDep,
) -> UserOut:
    repo = UserRepository(db)
    target = await repo.get_by_id(user_id)
    if target is None or target.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="User not found")
    changes = payload.model_dump(exclude_unset=True)
    if user.id == user_id:
        if "role" in changes and changes["role"] != user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role",
            )
        if "is_active" in changes and changes["is_active"] is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself",
            )
    for field, value in changes.items():
        setattr(target, field, value)
    try:
        await db.commit()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone already registered in this company",
        ) from exc
    await db.refresh(target)
    return UserOut.model_validate(target)


@router.post("/{user_id}/password", response_model=OkResponse)
async def reset_password(
    user_id: UUID,
    payload: PasswordResetRequest,
    user: AdminUser,
    db: DbDep,
) -> OkResponse:
    repo = UserRepository(db)
    target = await repo.get_by_id(user_id)
    if target is None or target.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="User not found")
    target.password_hash = hash_password(payload.password)
    await db.commit()
    return OkResponse()


@router.delete("/{user_id}", response_model=OkResponse)
async def delete_user(user_id: UUID, user: AdminUser, db: DbDep) -> OkResponse:
    if user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    repo = UserRepository(db)
    target = await repo.get_by_id(user_id)
    if target is None or target.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_active = False
    target.deleted_at = func.now()  # type: ignore[assignment]
    await db.commit()
    return OkResponse()
