# Water Delivery Management System (WDMS)

Suv yetkazib berish bizneslari uchun buyurtma, mijoz, to'lov va logistika avtomatlashtirish platformasi.

## Tuzilishi

```
water_delivery/
├── backend/   FastAPI + PostgreSQL + Redis + Celery
├── admin/     Vue 3 + Pinia + Vite  (keyingi bosqich)
├── driver/    React Native (Expo)   (keyingi bosqich)
└── pwa/       QR client (Vue 3/Vanilla) (keyingi bosqich)
```

## Tezkor ishga tushirish (Dev)

```bash
cp .env.example .env
docker compose up --build
```

- Backend: http://localhost:8017
- OpenAPI docs: http://localhost:8017/docs
- Health check: http://localhost:8017/health

## Release rejasi

- **R1 (Core MVP)** — auth, customers, orders, drivers, manual payments
- **R2 (Payments + QR)** — Payme, PWA, SMS OTP, Yandex Maps, GPS
- **R3 (Automation)** — Subscriptions, Telegram bot, reports

To'liq TZ: [`WDMS_TZ_v2.docx`](./WDMS_TZ_v2.docx)
