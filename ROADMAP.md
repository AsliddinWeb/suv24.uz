# Suv24 — keyingi yo'nalish (roadmap)

Tizim hozir to'liq ishlaydi. Quyidagilar — biznes va mahsulot bo'yicha *keyingi*
qadamlar, ta'siri va taxminiy ish hajmi bilan.

## 🚀 Sotuvni ko'paytirgich (1-2 hafta har biri)

### 1. Mijoz Telegram-bot — eng katta ta'sir
**Nima:** Mijoz `@suv24_demo_bot` ga "Salom" yozadi → bot uni telefon raqami orqali
ro'yxatdan o'tkazadi (yoki yangi mijoz qiladi) → "1 ta buyurtma berish" tugmasi → manzil
tanlash, mahsulot, miqdor → buyurtma operator panelida paydo bo'ladi va status (Yo'lda,
Yetkazildi) o'zgarganda mijozga avtomat xabar.

**Nega muhim:** App Store'siz, hech qanday o'rnatishsiz ishlaydi. O'zbekistonda
mijozlarning 90%+ Telegram ishlatadi. Buyurtmalarni 2-3x oshiradi va operatorni
qo'ng'iroq qabul qilish'dan ozod qiladi.

**Texnik:** `aiogram` (Python) yoki `node-telegram-bot-api`. Backend webhook endpoint
qabul qiladi. Har company'ga alohida bot token (Owner panelida sozlanadi).

---

### 2. Avto-obunalar (Recurring orders)
**Nima:** Mijoz "Har dushanba va payshanba 2 ta 19L" deb sozlasa, tizim avtomat
buyurtma yaratadi. Mijoz 1 marta sozlasa, abadiy davom etadi.

**Nega muhim:** Suv biznesi takroriy. Bu **predictable revenue** beradi va mijoz LTV'ni
2-5x oshiradi. Operator avtomatlashgan oqimni boshqaradi, qo'lda buyurtma kiritmaydi.

**Texnik:** Yangi `Subscription` jadvali (mijoz, mahsulot, sxema cron'lar bilan, faollik).
Celery beat task har soatda yangi buyurtmalarni yaratadi.

---

### 3. Payme integratsiyasi (real)
**Nima:** Mijoz Telegram bot yoki QR-kod orqali Payme bilan onlayn to'laydi → tizim
avtomatik to'lov yozadi → admin paneliga "+50k Payme" yoziladi.

**Nega muhim:** Landing'da va'da qildik. Yirik mijoz "Payme'siz olmaymiz" deyishi
tabiiy. Qarz muammosini ham hal qiladi (mijoz oldindan to'laydi).

**Texnik:** Payme Test Account → integration → Production. Payme API kichik, ~3 kun
kod + 1-2 hafta hujjat (legal entity, bank).

---

## 💎 Operatsion sifat (1 hafta har biri)

### 4. Driver push-notification
**Nima:** Yangi buyurtma kelganda haydovchi telefonida ovoz + bildirgich.

**Hozir:** App ochilganda yoki qayta fokuslanganda yangilanadi. Telefon stol ustida
yotganda haydovchi buyurtmani ko'rmaydi.

**Texnik:** Expo Push Notifications. Driver app `expo-notifications` push token oladi,
backend'ga yuboradi (`Driver.push_token` ustun), buyurtma tayinlanganda backend ushbu
tokenga push yuboradi. ~1 kun ish.

### 5. Mijozga SMS bildirgich (Eskiz)
**Nima:** "Buyurtmangiz #1234 yo'lda, taxminan 16:00 da yetkazamiz" — Eskiz SMS API
orqali avtomat.

**Nega muhim:** Mijoz qo'ng'iroq qilmaydi, ishonadi. Operator qo'shimcha vaqtidan
qutuladi. Eskiz API arzon va O'zbekistonda oddiy.

**Texnik:** Eskiz hisob → API token. Backend status_change event'da SMS yuboruvchi
service. ~1 kun.

### 6. Excel/PDF eksport
**Nima:** Buyurtmalar, to'lovlar, qarzlar, idish balansi — Excel/PDF eksport tugmasi.

**Nega muhim:** Har buxgalter so'raydi. Mijoz "menga oy oxirida hisobotni yuboring"
deydi. Bu birinchi sotuv argumentlardan biri.

**Texnik:** `openpyxl` Python kutubxonasi → `/api/v1/orders/export?format=xlsx`. ~yarim
kun ish.

---

## 📍 GPS va marshrut (qisman bajarildi)

### 7. ✅ Driver GPS tracking (bajarildi)
- Driver app har 30 soniyada koordinatani yuboradi
- Buyurtmalar masofa bo'yicha tartiblanadi (eng yaqindan)
- "Marshrutni xaritada" tugmasi — Yandex multi-stop yo'nalish

### 8. Admin live xarita (keyingi qadam)
**Nima:** Admin paneldagi xaritada hozir aktiv haydovchilarni real-time ko'rish.

**Nega muhim:** Operator "Aslan hozir qayerda?" — bir bosishda ko'radi. Mijozdan
"qachon yetib boradi?" qo'ng'irog'iga 5 sekundda javob beradi.

**Texnik:** Yandex Maps JS API embed + WebSocket yoki 30s polling drivers/list. ~2 kun.

### 9. Mijoz "Mening haydovchim" sahifasi
**Nima:** Mijoz buyurtma bergach, SMS yoki Telegram'da link oladi:
`suv24.uz/track/<token>` — haydovchi xaritada qayerda, qancha vaqtda yetadi.

**Nega muhim:** Mijoz xavotirsiz kutadi. Qo'ng'iroqlar 50% kamayadi.

**Texnik:** Public endpoint (token bilan), real-time GPS. ~1 kun.

---

## 🛡️ Production xavfsizligi

### 10. Postgres backup avtomati
deploy.md'da bor lekin haqiqatan ulanmagan. Cron yarating:
```cron
0 3 * * * docker exec wdms_postgres pg_dump -U wdms wdms | gzip > /var/backups/suv24/$(date +\%Y\%m\%d).sql.gz
0 4 * * * find /var/backups/suv24/ -mtime +30 -delete
```
Boshqa serverda mirror — masalan haftada bir Hetzner Storage Box'ga rsync.

### 11. Sentry DSN
`.env`'da `SENTRY_DSN=` bo'sh. Sentry'da loyihani yarating, DSN'ni qo'ying. Backend
allaqachon `sentry-sdk[fastapi]` o'rnatgan.

### 12. ✅ Tariff limit enforcement (bajarildi)
- Trial: 2 driver, 100 mijoz, 200 oylik buyurtma
- Start: 3 driver, 500 mijoz, 1000 oylik buyurtma
- Biznes / Premium: cheksiz
- Trial muddati tugaganda 402 Payment Required
- Settings sahifasida foydalanish ko'rinadi

### 13. SMS OTP login (Eskiz)
**Nima:** Telefon raqami → 6 xonali kod SMS → kirish. Parol o'rniga / parol bilan
birga.

**Nega muhim:** O'zbekistonda parolni unutish — keng tarqalgan muammo. SMS OTP
oddiyroq.

---

## 🎨 Mahsulot polish (har biri 1-2 kun)

### 14. Multi-til UI (uz/ru/uz-cyrl)
Toshkent mijozlari ruscha tushunadi. Vue I18n + tarjimalar.

### 15. Mijoz QR/sticker
Har mijoz uchun unique QR kod chop etib boring → keyingi safar haydovchi skanlasa,
darhol o'sha mijoz ro'yxatidan tushuradi (yangi buyurtma boshlash uchun bir tugma).

### 16. Loyalty / referral
"3 ta do'stingizni taklif qiling — 1 oy bepul" — viral o'sish.

### 17. Per-company custom domain (Premium va'da)
Premium tarif xaridorlariga `client1.suv24.uz` o'rniga o'z domeni
(`buyurtma.aquapro.uz`). DNS CNAME + SSL automation (cert-manager).

### 18. Customer rating
Mijoz buyurtma yetkazilgandan keyin haydovchini 1-5 baholaydi. Eng yaxshi haydovchilar
operatorga ko'rinadi.

---

## 📊 Mahsulot strategiyasi

### Mening tavsiyam — birinchi 30 kun
1. **1-hafta:** Telegram bot (eng katta ta'sir)
2. **2-hafta:** Avto-obunalar (LTV oshirish)
3. **3-hafta:** Push + SMS xabar (operatorni ozod qilish)
4. **4-hafta:** Admin live xarita + Excel eksport (sotuv argumenti)

Backup va Sentry birinchi kuni — zaruriyat, kechiktirmang.

### 60-90 kun
- Payme to'liq integratsiya
- Mijoz "Mening haydovchim" sahifasi
- Multi-til
- Per-company custom domain (Premium uchun)

### 6 oy
- Loyalty program
- 1C integratsiya (haqiqiy ehtiyoj bo'lganda)
- Mobile app for customers (PWA emas, native — Telegram bot yetarli bo'lmasa)

---

## Bajarilganlar (so'nggi sessiya)

- ✅ Driver GPS tracking + multi-stop Yandex marshrut + nearest-first sort
- ✅ Tariff limits enforcement (Trial/Start chegaralar) + Settings'da progress bar
- ✅ Sinov muddati tugaganda kirishni bloklash (402)
- ✅ Owner panelda "Mijoz arizalari" CRM
- ✅ Per-company brendlash (logo, nom, telefon)
- ✅ Multi-tenant platform owner
- ✅ Suv24.uz domain + SSL + production deploy
