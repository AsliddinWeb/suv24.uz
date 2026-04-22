# Buloq Haydovchi — Mobile App

Haydovchilar uchun React Native (Expo) ilova.

## Ishga tushirish

1. Dependencies o'rnatish:
```bash
cd driver
npm install
```

2. Backend IP manzilini sozlash (telefon Expo Go uchun):
```bash
cp .env.example .env
# .env da EXPO_PUBLIC_API_URL ni o'zgartiring:
# - iOS simulator: http://localhost:8017/api/v1
# - Android emulator: http://10.0.2.2:8017/api/v1
# - Haqiqiy telefon: http://<kompyuter-LAN-IP>:8017/api/v1
```

3. Dev serverni ishga tushirish:
```bash
npm start
```

4. Expo Go ilovasini (App Store / Play Store) yuklab oling va QR kodni skanerlang.

## Dev credentials

```
Telefon: +998933333333
Parol:   driver1234
```

Admin paneldan yangi haydovchi yaratsangiz, shu bilan ham kirishingiz mumkin.

## Ekranlar

- **Bugun** — bugungi buyurtmalar, filter (Biriktirilgan / Yo'lda / Yetkazildi), pull-to-refresh
- **Buyurtma detail** — mijoz (qo'ng'iroq), manzil (Yandex Maps), mahsulotlar, amallar
  - `Assigned` → **Yo'lga chiqdim**
  - `In delivery` → **Yetkazib berdim** (naqd + bo'sh idish) yoki **Yetkazib bo'lmadi** (sabab)
- **Idish** — haydovchining idish balansi (to'la / bo'sh har mahsulot bo'yicha)
- **Profil** — user info, chiqish

## Backend talablari

- Haydovchi user (`role: driver`) yaratilgan bo'lishi kerak
- Admin panelidan driver profil (vehicle_plate bilan) qo'shilgan
- Admin buyurtmani haydovchiga biriktirgan

## Stack

- Expo SDK 52 · Expo Router v4
- React Query (server state + cache)
- Zustand + AsyncStorage (auth)
- TypeScript strict
- Ionicons
