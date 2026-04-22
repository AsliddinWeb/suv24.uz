# Suv24 — production deploy (suv24.uz)

Production server'ga joylashtirish bo'yicha to'liq qo'llanma. Har bir qadam tekshirilgan
komanda beradi — nusxa ko'chiring va ishga tushiring.

## 0. Serverda nima bor, nima kerak

Talablar:

- Ubuntu 22.04+ yoki Debian 12+, minimum 2 vCPU / 4 GB RAM / 20 GB disk
- **Docker 24+** va **Docker Compose v2.24+** (`!reset`/`!override` override merge uchun)
- **Nginx** host'da (docker konteyneri emas) — boshqa loyihalar ham shu nginx orqali ketadi
- **certbot** — Let's Encrypt SSL uchun
- **Git**

Agar boshqa loyihalar `nginx-proxy` konteyneri ishlatsa, bu qo'llanmada **aksincha host nginx**
ishlatiladi — bitta serverda ko'p loyihani boshqarishning eng oson usuli.

Docker port konflikti — deploy.md'ning har bir joyida `BACKEND_HOST_PORT` o'zgaruvchisi
sizniki sifatida yo'naltiriladi (default 8017). Boshqa loyihangiz shu portni band qilgan
bo'lsa, `.env`'da boshqa raqam qo'ying (`BACKEND_HOST_PORT=8027` va h.k.).

## 1. DNS

`suv24.uz` domen registrar panelida **ikkita A-record** qo'shing:

| Turi  | Nom | Qiymat           |
|-------|-----|------------------|
| A     | @   | SERVER_PUBLIC_IP |
| A     | www | SERVER_PUBLIC_IP |

Tekshiring (mahalliy mashinadan):

```bash
dig +short suv24.uz
dig +short www.suv24.uz
```

Ikkalasi ham server IP qaytarishi kerak. DNS tarqalishi 5-60 daqiqa.

## 2. Serverga kerakli narsalarni o'rnatish

Bir marta serverda SSH orqali:

```bash
# Docker (agar yo'q bo'lsa)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# logout/login yoki `newgrp docker` qiling

# Nginx + certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# Cheklovlarni tekshirish (Node serverda kerak emas — admin container ichida build bo'ladi)
docker --version        # >= 24
docker compose version  # >= 2.24
nginx -v
```

## 3. Loyihani klon qilish

Deploy yo'li — `/home/projects/suv24.uz` (xohlagan joy bo'lishi mumkin, lekin nginx config shu yo'l bilan
yozilgan. Boshqa yo'l qilsangiz, nginx `root` direktivasini ham yangilang).

```bash
sudo mkdir -p /home/projects
sudo chown $USER:$USER /home/projects
cd /home/projects
git clone https://github.com/AsliddinWeb/suv24.uz.git suv24.uz
cd suv24.uz
```

## 4. Production `.env`

```bash
cp .env.production.example .env

# Kuchli sirlar yarat
openssl rand -hex 32    # JWT_SECRET_KEY ga
openssl rand -hex 24    # POSTGRES_PASSWORD ga

# Tahrir
nano .env
```

`.env`'da albatta o'zgartirilishi shart:

- `POSTGRES_PASSWORD` — random 24-hex
- `JWT_SECRET_KEY` — random 32-hex
- `SEED_OWNER_PHONE`, `SEED_OWNER_PASSWORD` — siz kira oladigan telefon + kuchli parol
- `SEED_ADMIN_PHONE`, `SEED_ADMIN_PASSWORD` — demo kompaniyaning birinchi super admini
- `BACKEND_HOST_PORT` — agar 8017 band bo'lsa, bo'sh portni qo'ying

`.env` faylingizni `chmod 600` qiling:

```bash
chmod 600 .env
```

## 5. Bitta komanda bilan ishga tushirish

Server'da `nodejs` o'rnatish ham kerak emas — admin frontend **container ichida quriladi**.

```bash
cd /home/projects/suv24.uz

# Hamma narsa: backend imidj + admin (node build + nginx) + postgres + redis
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Holat
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
# wdms_postgres   healthy
# wdms_redis      healthy
# wdms_backend    healthy
# wdms_admin      healthy

# Loglar
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
```

Avtomatik bajariladigan ishlar:
- Backend imidj quriladi, alembic migration'lar qo'llanadi, uvicorn 3 worker'da ishga tushadi
- Admin container node:20'da Vue SPA'ni build qiladi, nginx:alpine bilan xizmat qiladi
- `/api/` va `/media/` admin container'ning ichidan backend'ga proxy bo'ladi
- Postgres/redis portlar faqat docker tarmoqda, hostga chiqmaydi

**Seed (birinchi ishga tushirish):**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec backend python -m app.cli.seed
```

Bu `.env`'da yozilgan owner va demo admin foydalanuvchilarini yaratadi.

**Lokal tekshiruv** (host nginx hali yo'q):

```bash
curl -s http://127.0.0.1:8020/        # admin SPA HTML
curl -s http://127.0.0.1:8020/api/v1/health   # {"status":"ok"}
```

## 6. Nginx config + SSL

Config'da faqat HTTP (port 80) bor — certbot ishga tushgach, SSL direktivalarini
(listen 443, ssl_certificate, HTTP→HTTPS redirect) avtomat qo'shadi.

```bash
# Config nusxasini nginx'ga o'rnatish
sudo cp /home/projects/suv24.uz/nginx/suv24.uz /etc/nginx/sites-available/suv24.uz

# Agar ADMIN_HOST_PORT 8020 dan boshqa bo'lsa — config'da ham o'zgartiring
# sudo sed -i 's|127.0.0.1:8020|127.0.0.1:9020|g' /etc/nginx/sites-available/suv24.uz

# Enable
sudo ln -s /etc/nginx/sites-available/suv24.uz /etc/nginx/sites-enabled/

# Sintaksis tekshir va reload
sudo nginx -t
sudo systemctl reload nginx
```

Endi http://suv24.uz ochilishi kerak. Keyin SSL:

```bash
sudo certbot --nginx -d suv24.uz -d www.suv24.uz \
  --agree-tos --email YOUR@EMAIL.UZ --no-eff-email --redirect
```

Certbot avtomatik qiladi:
- Let's Encrypt sertifikatini oladi
- Config'ga `listen 443 ssl`, `ssl_certificate`, `ssl_certificate_key` qo'shadi
- HTTP (80) → HTTPS (443) redirect qo'shadi
- Nginx'ni reload qiladi

Natijani ko'rish:

```bash
sudo cat /etc/nginx/sites-available/suv24.uz
```

## 7. Tekshirish

```bash
# HTTPS ishlashi kerak
curl -sI https://suv24.uz          # HTTP/2 200
curl -sI https://www.suv24.uz      # 301 → suv24.uz
curl -s https://suv24.uz/api/v1/health   # {"status":"ok"} yoki 404

# Brauzerdan
# https://suv24.uz — landing sahifa
# https://suv24.uz/login — login formasi
# https://suv24.uz/platform — owner panel (owner parol bilan)
```

SSL sifati: https://www.ssllabs.com/ssltest/analyze.html?d=suv24.uz — A yoki A+ bo'lishi kerak.

## 8. SSL avtomatik yangilanishi

Certbot o'rnatishda sistemd timer ham o'rnatadi — tekshiring:

```bash
systemctl list-timers | grep certbot
sudo certbot renew --dry-run
```

Har 90 kunda avtomat yangilaydi.

## 9. Driver ilova

`driver/.env` serverda kerak emas — bu mobil ilova, telefonda ishlaydi. `EXPO_PUBLIC_API_URL`'ni
production bilan qurganingizda (EAS Build) `https://suv24.uz/api/v1` ga yo'naltiring:

```bash
cd driver
# eas.json da yoki build komandasida:
EXPO_PUBLIC_API_URL=https://suv24.uz/api/v1 eas build --platform ios --profile production
```

## 10. Backup

**Postgres dumpni har kuni:**

`/etc/cron.d/suv24-backup` yarating:

```cron
0 3 * * * root docker exec wdms_postgres pg_dump -U wdms wdms | gzip > /var/backups/suv24/$(date +\%Y\%m\%d).sql.gz
0 4 * * * root find /var/backups/suv24/ -mtime +30 -delete
```

```bash
sudo mkdir -p /var/backups/suv24
sudo chmod 700 /var/backups/suv24
```

**Media volume** (logotiplari):

```bash
# Backup
docker run --rm -v water_delivery_wdms_media:/data -v /var/backups/suv24:/backup alpine \
  tar czf /backup/media-$(date +%Y%m%d).tar.gz -C /data .
```

## 11. Yangilash

```bash
cd /home/projects/suv24.uz
git pull origin main

# Bitta komanda: yangi kodlar bilan backend + admin qayta quriladi va ko'tariladi
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Agar nginx config o'zgartirgan bo'lsangiz:
sudo cp nginx/suv24.uz /etc/nginx/sites-available/suv24.uz
sudo nginx -t && sudo systemctl reload nginx
```

Zero-downtime deploy uchun alohida servis yangilash: `up -d --no-deps --build admin`
yoki `--build backend` — eski konteyner bitgach yangisi o'rniga keladi.

## 12. Monitoring

- **Loglar**: `docker compose logs -f backend` — real-time
- **Sentry**: `.env`'da `SENTRY_DSN` to'ldirsangiz, exception'lar avtomat yuboriladi
- **Holat tekshiruvi**: `/health` va `/ready` endpoint'lari
- **Resurs**: `docker stats` — CPU/RAM har konteyner uchun

## 13. Muammolarni bartaraf qilish

**Backend 502 xato beradi**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail 100 backend
curl http://127.0.0.1:8017/health
```

Ko'rinmasa — port band yoki konteyner yiqilgan. `.env`'da `BACKEND_HOST_PORT` boshqa porta
o'zgartiring va nginx config'ni ham yangilang.

**Migration xato bo'ldi**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec backend alembic current
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec backend alembic upgrade head
```

**Boshqa loyiha ham bor — postgres port konflikti**

Prod compose postgres host portini olib tashladi (`ports: !reset []`), shuning uchun konflikt
bo'lmasligi kerak. Agar boshqa `wdms_postgres` nomli konteyner bo'lsa, `container_name`'ni
o'zgartiring yoki boshqa loyihani qayta nomlang.

**Cross-origin/CORS xato**

`.env`'da `CORS_ORIGINS=https://suv24.uz,https://www.suv24.uz` to'g'ri kiritilganini
tekshiring, backend'ni qayta ishga tushiring.

**Logo yuklash ishlamayapti**

- Nginx `client_max_body_size 8m` borligini tekshiring
- Backend `/app/media/logos/` papkasi yozuvga ochiqligini tekshiring
- Docker named volume `wdms_media` mount qilinganligini tekshiring:
  `docker inspect wdms_backend | grep -A 3 media`

## 14. Birinchi kirish

1. https://suv24.uz/login
2. `.env`'dagi `SEED_OWNER_PHONE` va `SEED_OWNER_PASSWORD` bilan kiring
3. `/platform` panelga avtomat yo'naltiradi
4. **Kompaniyalar** → **Yangi kompaniya** — birinchi mijozni yarating
5. Mijoz super admini shu formada yaratilgan telefon+parol bilan `/login`'ga kiradi

Tayyor.

---

## Maslahatlar

- **Parollarni o'zgartirish**: birinchi kirishdan keyin `.env`'dagi seed parollarni
  o'chiring (ular kerak emas), haqiqiy parolingizni admin panelda o'rnating
- **Birinchi marta ishga tushirish**: seed'dan keyin `SEED_OWNER_*` va `SEED_ADMIN_*`
  env'larni `.env`'dan olib tashlashingiz mumkin
- **Boshqa loyihalar bilan nginx**: har loyiha uchun alohida `sites-available/*.conf`
  yarating, hammasi bir nginx orqali ketadi
