<h1 align="center">🏠 UyIjara</h1>

<p align="center">
  <b>Maklersiz uy ijara platformasi</b><br>
  Uy egasi va ijarachi orasida to‘g‘ridan-to‘g‘ri aloqa — vositachisiz.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/i18n-uz%20%7C%20ru%20%7C%20en-7c3aed" alt="i18n">
  <img src="https://img.shields.io/badge/license-private-orange" alt="license">
</p>

---

## 💡 Loyiha haqida

**UyIjara** — O‘zbekistonda uy ijaraga berish va olish uchun mo‘ljallangan onlayn platforma. Foydalanuvchi premium tarif sotib oladi va uy egasiga **to‘g‘ridan-to‘g‘ri** qo‘ng‘iroq qiladi. Hech qanday makler, hech qanday vositachi haq.

> **Maqsad:** Maklersiz, oddiy va ishonchli ijara bozori yaratish.

---

## ✨ Asosiy imkoniyatlar

| | |
|--|--|
| 🌐 **3 til** | O‘zbekcha, Русский, English — sahifa joyida tarjima qilinadi |
| 📱 **Mobile-first** | Pastki tab navigatsiya, swipe galereya, touch-friendly |
| 💳 **Premium tariflar** | 3 va 7 kunlik obuna, balans yoki karta orqali to‘lov |
| 📞 **To‘g‘ridan-to‘g‘ri qo‘ng‘iroq** | `tel:` linki bilan bir bosishda qo‘ng‘iroq |
| 🗺️ **Interaktiv xarita** | OpenStreetMap orqali aniq joylashuv |
| 🖼️ **Galereya** | Strelka + swipe + lightbox |
| ⭐ **Reyting va izohlar** | 1–5 yulduz, foydalanuvchi izohlari |
| ❤️ **Saqlangan uylar** | AJAX wishlist |
| 🚩 **Shikoyat tizimi** | 5+ shikoyat — avtomatik blok |
| 📊 **Admin dashboard** | Real-time statistika, Chart.js grafikalar |
| 🔌 **JSON API** | Mobile app uchun tayyor (`/api/`) |

---

## 🛠️ Texnologiyalar

```
Backend       Django 6 · Python 3.11+
Database      SQLite (dev) · PostgreSQL (prod)
Frontend      HTML + CSS + Vanilla JS · Chart.js
Map           Leaflet + OpenStreetMap
i18n          Django i18n + polib
Static        WhiteNoise
```

---

## 🚀 Tezkor ishga tushirish

```bash
# 1. Klonlash
git clone <repo-url> uyijara && cd uyijara

# 2. Virtual muhit
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# 3. Paketlar
pip install -r requirements.txt

# 4. Migratsiya + ma'lumot
python manage.py migrate
python manage.py fill_translations    # ru/en region nomlari
python manage.py createsuperuser

# 5. Server
python manage.py runserver 8080
```

🌐 **Saytni oching:** <http://127.0.0.1:8080/>
🔧 **Admin panel:** <http://127.0.0.1:8080/users/admin-dashboard/>

---

## 📁 Tuzilishi

```
.
├── config/              # ⚙️  Settings, URL, til o‘zgartirgich
├── houses/              # 🏠  Uy + region/district + comments + wishlist
│   ├── api.py           # 🔌  JSON API
│   └── management/
├── users/               # 👥  User + Tariff + Payment + Notification
│   └── signals.py       # ⚡  Avtoblok (5+ shikoyat)
├── tepmlates/           # 📄  HTML shablonlar
│   ├── base.html        # navbar + mobile bottom nav + til tugmasi
│   ├── houses/          # uy sahifalari
│   ├── users/           # profil/auth/tariflar
│   └── admin_custom/    # 🎨  Custom admin panel
├── locale/              # 🌐  uz/ru/en .po + .mo
├── static/  media/
├── requirements.txt
└── .env.example
```

---

## 🌐 Til boshqaruvi

3 ta til mavjud: **O‘zbekcha**, **Русский**, **English**.

| URL prefiksi | Til |
|--------------|-----|
| `/`          | uz (default) |
| `/ru/`       | Русский      |
| `/en/`       | English      |

Til tugmasi bosilganda **xuddi shu sahifa** yangi tilga o‘tadi:
`/users/login/` → `/ru/users/login/` → `/en/users/login/`

Region va tuman nomlari ham bazada 3 tilda saqlanadi:
- 🇺🇿 Buxoro viloyati
- 🇷🇺 Бухарская область
- 🇬🇧 Bukhara Region

---

## 🔌 JSON API (mobile app uchun)

DRF talab qilmaydigan engil JsonResponse-based endpointlar:

| Method | URL | Tavsif |
|--------|-----|--------|
| `GET`  | `/api/houses/` | Uylar ro‘yxati (filter + pagination) |
| `GET`  | `/api/houses/<id>/` | Uy detali |
| `POST` | `/api/houses/<id>/wishlist/` | Saqlash/olib tashlash |
| `GET`  | `/api/regions/` | Viloyatlar |
| `GET`  | `/api/districts/?region_id=N` | Tumanlar |
| `GET`  | `/api/me/` | Joriy foydalanuvchi |

**Filter parametrlari** (`/api/houses/`): `region`, `min_price`, `max_price`, `q`, `sort` (cheap/expensive/top), `page`.

---

## ⚙️ Sozlamalar (`.env`)

`.env.example` dan nusxa ko‘chiring va kerakli qiymatlarni kiriting:

```ini
DJANGO_SECRET_KEY=<long-random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=uyijara.uz,www.uyijara.uz
DJANGO_EMAIL_HOST_USER=info@uyijara.uz
DJANGO_EMAIL_HOST_PASSWORD=<smtp-app-pass>
```

`DEBUG=False` da avtomatik yoqiladi: HSTS, secure cookies, X-Frame=DENY, WhiteNoise compressed manifest.

---

## 📋 Foydali buyruqlar

```bash
python manage.py runserver 8080         # Dev server
python manage.py migrate                # Migratsiya
python manage.py fill_translations      # Region/tuman tarjimalari
python manage.py create_test_data       # Test ma'lumot
python locale/generate_translations.py  # .po + .mo generatsiya
python manage.py collectstatic          # Static fayllar (prod)
python manage.py check --deploy         # Production xavfsizlik tekshiruvi
```

---

## 🚢 Production deploy

```bash
# 1. Server tayyorlash
pip install gunicorn psycopg2-binary

# 2. Static collect
python manage.py collectstatic --noinput

# 3. Gunicorn
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

**Nginx** orqali reverse proxy qiling, **PostgreSQL** ishlatib, **Let’s Encrypt** SSL o‘rnating.

---

## 📱 Mobil ilova rejasi

Web qismi mobile-friendly bo‘lishidan tashqari:

- ✅ JSON API tayyor (`/api/`)
- 🔜 Token-based auth (DRF + SimpleJWT)
- 🔜 Push bildirishnoma (FCM)
- 🔜 Flutter / React Native client

---

## 👤 Muallif

**Umid Jorayev** · UyIjara startup · 📧 umidjorayev091@gmail.com

---

<p align="center">
  <sub>🚀 Built with Django · MIT-style private use · 2026</sub>
</p>
