from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import func, select

from app.core.deps import CurrentUser, DbDep
from app.core.rate_limit import limiter
from app.models.lead import Lead, LeadStatus
from app.models.user import User, UserRole
from app.schemas.lead import LeadAck, LeadCreate, LeadOut, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


# ---------- PUBLIC: landing form submits here ----------

@router.post("", response_model=LeadAck, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def submit_lead(
    request: Request, response: Response, payload: LeadCreate, db: DbDep
) -> LeadAck:
    """No auth. Rate-limited so bots can't flood the CRM inbox."""
    phone = payload.phone.strip()
    # Dedupe: if the same phone already submitted a NEW lead in the last 24h, just
    # acknowledge instead of creating a duplicate row.
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=1)
    recent = (
        await db.execute(
            select(Lead).where(
                Lead.phone == phone,
                Lead.status == LeadStatus.NEW,
                Lead.deleted_at.is_(None),
                Lead.created_at > cutoff,
            )
        )
    ).scalar_one_or_none()
    if recent is not None:
        return LeadAck(id=recent.id)

    lead = Lead(
        full_name=payload.full_name.strip(),
        phone=phone,
        company_name=(payload.company_name or "").strip() or None,
        notes=(payload.notes or "").strip() or None,
        source=payload.source,
        status=LeadStatus.NEW,
    )
    db.add(lead)
    await db.flush()
    await db.commit()
    await db.refresh(lead)
    return LeadAck(id=lead.id)


# ---------- PRIVATE: platform owner only ----------

async def _require_owner(user: CurrentUser) -> User:
    if user.role != UserRole.PLATFORM_OWNER:
        raise HTTPException(status_code=403, detail="Platform owner only")
    return user


PlatformOwner = Annotated[User, Depends(_require_owner)]


@router.get("", response_model=list[LeadOut])
async def list_leads(
    _: PlatformOwner,
    db: DbDep,
    status_filter: LeadStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
) -> list[LeadOut]:
    stmt = select(Lead).where(Lead.deleted_at.is_(None)).order_by(Lead.created_at.desc())
    if status_filter is not None:
        stmt = stmt.where(Lead.status == status_filter)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            (func.lower(Lead.full_name).like(like))
            | (Lead.phone.like(f"%{q}%"))
            | (func.lower(func.coalesce(Lead.company_name, "")).like(like))
        )
    rows = (await db.execute(stmt)).scalars().all()
    return [LeadOut.model_validate(r) for r in rows]


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: UUID, _: PlatformOwner, db: DbDep) -> LeadOut:
    lead = (
        await db.execute(select(Lead).where(Lead.id == lead_id, Lead.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadOut.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: UUID,
    payload: LeadUpdate,
    _: PlatformOwner,
    db: DbDep,
) -> LeadOut:
    lead = (
        await db.execute(select(Lead).where(Lead.id == lead_id, Lead.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    await db.flush()
    await db.commit()
    await db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: UUID, _: PlatformOwner, db: DbDep) -> Response:
    lead = (
        await db.execute(select(Lead).where(Lead.id == lead_id, Lead.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.deleted_at = datetime.now(tz=timezone.utc)
    await db.commit()
    return Response(status_code=204)
