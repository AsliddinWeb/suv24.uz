from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUser, DbDep, require_roles
from app.core.security import hash_password
from app.models.driver import Driver
from app.models.user import User, UserRole
from app.repositories.driver import DriverRepository
from app.repositories.user import UserRepository
from app.schemas.common import OkResponse
from app.schemas.driver import DriverCreate, DriverOut, DriverUpdate, DriverWithUserOut

router = APIRouter(prefix="/drivers", tags=["drivers"])

AdminUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
]


def _with_user(driver: Driver) -> DriverWithUserOut:
    return DriverWithUserOut(
        id=driver.id,
        company_id=driver.company_id,
        user_id=driver.user_id,
        vehicle_plate=driver.vehicle_plate,
        is_active=driver.is_active,
        current_lat=driver.current_lat,
        current_lng=driver.current_lng,
        last_seen_at=driver.last_seen_at,
        full_name=driver.user.full_name,
        phone=driver.user.phone,
    )


@router.get("", response_model=list[DriverWithUserOut])
async def list_drivers(
    user: CurrentUser,
    db: DbDep,
    only_active: bool = Query(default=False),
) -> list[DriverWithUserOut]:
    repo = DriverRepository(db)
    if user.role == UserRole.DRIVER:
        own = await repo.get_by_user_id(user.company_id, user.id)
        return [_with_user(own)] if own else []
    drivers = await repo.list_all(user.company_id, only_active=only_active)
    return [_with_user(d) for d in drivers]


@router.get("/me", response_model=DriverWithUserOut)
async def get_me(user: CurrentUser, db: DbDep) -> DriverWithUserOut:
    if user.role != UserRole.DRIVER:
        raise HTTPException(status_code=404, detail="Not a driver account")
    driver = await DriverRepository(db).get_by_user_id(user.company_id, user.id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    return _with_user(driver)


@router.post("", response_model=DriverWithUserOut, status_code=status.HTTP_201_CREATED)
async def create_driver(
    payload: DriverCreate,
    user: AdminUser,
    db: DbDep,
) -> DriverWithUserOut:
    """Create a new driver: provisions a User(role=driver) and Driver profile in one step."""
    users = UserRepository(db)
    drivers = DriverRepository(db)

    existing_user = await users.get_by_phone(user.company_id, payload.phone)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu telefon raqami band",
        )

    new_user = User(
        company_id=user.company_id,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=UserRole.DRIVER,
        is_active=True,
    )
    db.add(new_user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu telefon raqami band",
        )

    driver = Driver(
        company_id=user.company_id,
        user_id=new_user.id,
        vehicle_plate=payload.vehicle_plate,
        is_active=True,
    )
    db.add(driver)
    await db.flush()
    await db.commit()
    await db.refresh(driver)
    return _with_user(driver)


@router.get("/{driver_id}", response_model=DriverWithUserOut)
async def get_driver(driver_id: UUID, user: CurrentUser, db: DbDep) -> DriverWithUserOut:
    driver = await DriverRepository(db).get(user.company_id, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return _with_user(driver)


@router.patch("/{driver_id}", response_model=DriverWithUserOut)
async def update_driver(
    driver_id: UUID,
    payload: DriverUpdate,
    user: AdminUser,
    db: DbDep,
) -> DriverWithUserOut:
    drivers = DriverRepository(db)
    driver = await drivers.get(user.company_id, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")

    changes = payload.model_dump(exclude_unset=True)
    # Fields that live on the linked User
    user_fields = {"full_name", "phone", "password"}
    user_changes = {k: v for k, v in changes.items() if k in user_fields}
    driver_changes = {k: v for k, v in changes.items() if k not in user_fields}

    if user_changes:
        target_user = driver.user
        if "phone" in user_changes and user_changes["phone"] != target_user.phone:
            clashing = await UserRepository(db).get_by_phone(user.company_id, user_changes["phone"])
            if clashing is not None and clashing.id != target_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Bu telefon raqami band",
                )
            target_user.phone = user_changes["phone"]
        if "full_name" in user_changes:
            target_user.full_name = user_changes["full_name"]
        if "password" in user_changes:
            target_user.password_hash = hash_password(user_changes["password"])

    for field, value in driver_changes.items():
        setattr(driver, field, value)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Konflikt")

    await db.commit()
    await db.refresh(driver)
    return _with_user(driver)


@router.delete("/{driver_id}", response_model=OkResponse)
async def delete_driver(driver_id: UUID, user: AdminUser, db: DbDep) -> OkResponse:
    drivers = DriverRepository(db)
    driver = await drivers.get(user.company_id, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")

    now = datetime.now(tz=timezone.utc)
    driver.deleted_at = now
    driver.is_active = False
    # Also deactivate the underlying User so they can't log in via driver app
    driver.user.is_active = False
    driver.user.deleted_at = now

    await db.commit()
    return OkResponse()
