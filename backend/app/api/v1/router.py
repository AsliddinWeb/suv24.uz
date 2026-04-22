from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.companies import router as companies_router
from app.api.v1.customers import router as customers_router
from app.api.v1.drivers import router as drivers_router
from app.api.v1.bottles import router as bottles_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.platform import router as platform_router
from app.api.v1.products import router as products_router
from app.api.v1.reports import router as reports_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(platform_router)
api_router.include_router(companies_router)
api_router.include_router(users_router)
api_router.include_router(customers_router)
api_router.include_router(products_router)
api_router.include_router(drivers_router)
api_router.include_router(bottles_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(reports_router)


@api_router.get("/ping", tags=["system"])
async def ping() -> dict[str, str]:
    return {"pong": "ok"}
