from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import CurrentUser, DbDep, require_roles
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
    # Driver sees only their own profile
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
    users = UserRepository(db)
    drivers = DriverRepository(db)

    target_user = await users.get_by_id(payload.user_id)
    if target_user is None or target_user.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user must have role=driver",
        )
    existing = await drivers.get_by_user_id(user.company_id, target_user.id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Driver profile already exists")

    driver = await drivers.create(
        Driver(
            company_id=user.company_id,
            user_id=target_user.id,
            vehicle_plate=payload.vehicle_plate,
            is_active=True,
        )
    )
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
    for field, value in changes.items():
        setattr(driver, field, value)
    await db.commit()
    await db.refresh(driver)
    return _with_user(driver)


@router.delete("/{driver_id}", response_model=OkResponse)
async def delete_driver(driver_id: UUID, user: AdminUser, db: DbDep) -> OkResponse:
    drivers = DriverRepository(db)
    driver = await drivers.get(user.company_id, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    await drivers.delete(driver)
    await db.commit()
    return OkResponse()
