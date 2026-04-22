import secrets
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.deps import CurrentUser, DbDep, require_roles
from app.models.user import User, UserRole
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyOut, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])

StaffAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
]

MEDIA_ROOT = Path("/app/media")
LOGO_DIR = MEDIA_ROOT / "logos"
ALLOWED_LOGO_TYPES = {"image/png", "image/jpeg", "image/webp", "image/svg+xml"}
LOGO_MAX_BYTES = 2 * 1024 * 1024  # 2 MB
EXT_FOR_TYPE = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}


@router.get("/me", response_model=CompanyOut)
async def get_my_company(user: CurrentUser, db: DbDep) -> CompanyOut:
    repo = CompanyRepository(db)
    company = await repo.get_by_id(user.company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return CompanyOut.model_validate(company)


@router.patch("/me", response_model=CompanyOut)
async def update_my_company(
    payload: CompanyUpdate,
    user: StaffAdmin,
    db: DbDep,
) -> CompanyOut:
    repo = CompanyRepository(db)
    company = await repo.get_by_id(user.company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(company, field, value)

    await db.flush()
    await db.commit()
    await db.refresh(company)
    return CompanyOut.model_validate(company)


@router.post("/me/logo", response_model=CompanyOut)
async def upload_my_company_logo(
    user: StaffAdmin,
    db: DbDep,
    file: UploadFile = File(...),
) -> CompanyOut:
    if file.content_type not in ALLOWED_LOGO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="PNG, JPG, WebP yoki SVG yuklang",
        )
    data = await file.read()
    if len(data) > LOGO_MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Fayl 2 MB dan katta bo'lmasligi kerak",
        )

    repo = CompanyRepository(db)
    company = await repo.get_by_id(user.company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    ext = EXT_FOR_TYPE[file.content_type]
    filename = f"{company.slug}-{secrets.token_hex(4)}{ext}"
    dest = LOGO_DIR / filename
    dest.write_bytes(data)

    # Store a relative path; admin and driver clients prefix their API origin when rendering.
    company.logo_url = f"/media/logos/{filename}"

    await db.flush()
    await db.commit()
    await db.refresh(company)
    return CompanyOut.model_validate(company)
