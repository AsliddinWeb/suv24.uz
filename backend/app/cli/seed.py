"""Dev seeder: default company + super admin user.

Run via:
    docker compose exec backend python -m app.cli.seed
"""
import asyncio
import os
import sys

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models.company import Company
from app.models.user import User, UserRole
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository


DEFAULT_ADMIN_PHONE = os.getenv("SEED_ADMIN_PHONE", "+998900000000")
DEFAULT_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin12345")
DEFAULT_ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "Super Admin")
DEFAULT_COMPANY_NAME = os.getenv("SEED_COMPANY_NAME", "Demo Suv Kompaniyasi")


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        companies = CompanyRepository(db)
        users = UserRepository(db)

        company = await companies.get_by_slug(settings.DEFAULT_COMPANY_SLUG)
        if company is None:
            company = await companies.create(
                Company(
                    name=DEFAULT_COMPANY_NAME,
                    slug=settings.DEFAULT_COMPANY_SLUG,
                    timezone=settings.APP_TIMEZONE,
                    currency="UZS",
                    is_active=True,
                )
            )
            print(f"[seed] created company: {company.slug}")
        else:
            print(f"[seed] company already exists: {company.slug}")

        admin = await users.get_by_phone(company.id, DEFAULT_ADMIN_PHONE)
        if admin is None:
            admin = await users.create(
                User(
                    company_id=company.id,
                    phone=DEFAULT_ADMIN_PHONE,
                    password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                    full_name=DEFAULT_ADMIN_NAME,
                    role=UserRole.SUPER_ADMIN,
                    is_active=True,
                )
            )
            await db.commit()
            print(f"[seed] created super admin: {admin.phone}")
            print(f"[seed] password: {DEFAULT_ADMIN_PASSWORD}")
        else:
            print(f"[seed] super admin already exists: {admin.phone}")

    await engine.dispose()


def main() -> None:
    try:
        asyncio.run(seed())
    except Exception as exc:  # pragma: no cover
        print(f"[seed] FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
