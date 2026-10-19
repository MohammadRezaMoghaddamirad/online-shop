# Online Shop API (Django REST Framework)
https://online-shop-delta-sandy.vercel.app/

فروشگاه آنلاین با دو نقش **Customer** و **Admin**، احراز هویت JWT، سبد خرید، کد تخفیف، سفارش و مدیریت موجودی.

## راه‌اندازی با Docker (پیشنهادی)

```bash
cp .env.example .env.dev          # سپس SECRET_KEY و DB_PASSWORD را عوض کنید
cp .env.example .env              # فقط DB_NAME / DB_USER / DB_PASSWORD برای docker compose
docker compose up --build         # migrate به‌صورت خودکار اجرا می‌شود
docker compose exec web python manage.py createsuperuser
docker compose exec web pytest    # اجرای تست‌ها
```

- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/
- Django Admin: http://127.0.0.1:8000/admin/

## راه‌اندازی محلی (بدون Docker)

نیاز به PostgreSQL دارد. متغیرها از فایل `.env` (یا هر env دیگر) خوانده می‌شوند.

```bash
python -m venv .venv && source .venv/bin/activate     # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
pytest
```

## متغیرهای محیطی

| متغیر | توضیح | پیش‌فرض |
|---|---|---|
| `DEBUG` | حالت توسعه | `True` |
| `SECRET_KEY` | کلید Django (وقتی `DEBUG=False` است اجباری) | کلید توسعه |
| `ALLOWED_HOSTS` | با کاما جدا شود | `*` در حالت DEBUG |
| `DB_ENGINE` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | تنظیمات دیتابیس | `postgresql` / `shop_db` / `postgres` / خالی / `localhost` / `5432` |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | آدرس Redis | `redis://localhost:6379/0` |
| `CORS_ALLOWED_ORIGINS` | با کاما جدا شود | localhost:3000 و 5173 |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` / `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | طول عمر توکن‌ها | `30` / `7` |

هزینه ارسال ثابت است و در `config/settings.py` با `SHOP_SHIPPING_COST` (پیش‌فرض ۵۰٬۰۰۰) تنظیم می‌شود.

احراز هویت: هدر `Authorization: Bearer <access_token>`

## Endpointها

همه مسیرها با پیشوند `/api/v1/` هستند.

| متد | مسیر | دسترسی | توضیح |
|---|---|---|---|
| POST | `auth/register/` | همه | ثبت‌نام (همیشه Customer) |
| POST | `auth/login/` | همه | دریافت `access` و `refresh` |
| POST | `auth/token/refresh/` | همه | تمدید توکن (چرخش و blacklist) |
| POST | `auth/logout/` | کاربر | body: `{"refresh": "..."}` |
| GET/PUT/PATCH | `accounts/profile/` | کاربر | مشاهده و ویرایش پروفایل خود |
| GET | `categories/`، `categories/{id}/` | همه | مشتری فقط دسته‌های فعال را می‌بیند |
| POST/PUT/PATCH/DELETE | `categories/...` | Admin | مدیریت دسته‌بندی |
| GET | `products/`، `products/{id}/` | همه | فقط محصولات فعال از دسته‌های فعال |
| POST/PUT/PATCH/DELETE | `products/...` | Admin | مدیریت محصول |
| PATCH | `products/{id}/stock/` | Admin | تغییر موجودی `{"stock": 20}` |
| GET | `carts/` | کاربر | مشاهده سبد و قیمت نهایی |
| POST | `carts/add/` | کاربر | `{"product_id": 1, "quantity": 2}` |
| PATCH | `carts/items/{id}/` | کاربر | `{"quantity": 3}` |
| DELETE | `carts/items/{id}/remove/` | کاربر | حذف یک آیتم |
| DELETE | `carts/clear/` | کاربر | خالی کردن سبد |
| POST | `orders/checkout/` | کاربر | ثبت سفارش `{"coupon_code": "SUMMER20"}` (اختیاری) |
| GET | `orders/`، `orders/{id}/` | کاربر | فقط سفارش‌های خود کاربر |
| GET | `orders/admin/`، `orders/admin/{id}/` | Admin | همه سفارش‌ها (`?status=&user=`) |
| PATCH | `orders/admin/{id}/status/` | Admin | `{"status": "paid"}` |
| GET/POST/PUT/PATCH/DELETE | `coupons/...` | Admin | مدیریت کد تخفیف |
| GET/PATCH/DELETE ... | `accounts/users/...` | Admin | مشاهده کاربران، تغییر `role` و `is_active` |

**محصولات:** `?category=<id>` فیلتر دسته، `?search=` جستجو در نام و توضیحات، `?ordering=price` یا `?ordering=-price` مرتب‌سازی (`price`، `name`، `created_at`، `stock`).

**Pagination:** `?page=2` و `?page_size=20` (حداکثر ۱۰۰، پیش‌فرض ۱۰).

## تصمیم‌های طراحی

- **Checkout اتمیک**: همه مراحل داخل `transaction.atomic()` و با `select_for_update()` (روی PostgreSQL قفل واقعی).
- **همه محاسبات سمت سرور است**: جمع کالاها، تخفیف، هزینه ارسال و مبلغ نهایی. مشتری فقط کد تخفیف می‌فرستد.
- **Snapshot سفارش**: `OrderItem` نام و قیمت محصول را هنگام خرید ذخیره می‌کند؛ تغییر یا حذف محصول روی سفارش قبلی اثر ندارد.
- **کد تخفیف**: بررسی وجود، فعال بودن، انقضا، حداقل مبلغ و مصرف قبلی توسط همان کاربر.
- **وضعیت سفارش**: گذارهای مجاز `pending → paid → processing → shipped → delivered`. لغو فقط از `pending` / `paid` / `processing` ممکن است. لغو، موجودی را برمی‌گرداند و کد تخفیف را آزاد می‌کند. وضعیت فقط از مسیر `orders/admin/{id}/status/` تغییر می‌کند.
- **محصول قابل فروش**: محصول و دسته‌بندی‌اش هر دو باید فعال باشند. افزودن محصول بدون موجودی یا بیشتر از موجودی به سبد خطا می‌دهد.
- **حذف دسته‌بندی** که محصول دارد (`PROTECT`) با خطای 409 رد می‌شود.
- **قالب خطا** (برای همه خطاها): `{"success": false, "error": {"code", "message", "details"}}`
- **مبالغ** به‌صورت عدد صحیح (تومان) ذخیره می‌شوند.
- **انتخاب View**: `ModelViewSet` برای CRUD ادمین، `ReadOnlyModelViewSet` برای مشاهده سفارش‌ها، `generics` برای Register و Profile، `ViewSet` برای سبد خرید، `GenericAPIView` برای Logout.
