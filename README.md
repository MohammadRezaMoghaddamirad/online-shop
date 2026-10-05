# Online Shop API (Django REST Framework)

فروشگاه آنلاین با دو نقش **Customer** و **Admin**، احراز هویت JWT، سبد خرید، کد تخفیف، سفارش و مدیریت موجودی.

## راه‌اندازی

```bash
python -m venv .venv && source .venv/bin/activate     # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations users catalog cart coupons orders
python manage.py migrate
python manage.py createsuperuser          # superuser به‌صورت خودکار role=admin می‌گیرد
python manage.py runserver

python manage.py test                     # اجرای تست‌ها
```

- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/
- Django Admin (اختیاری): http://127.0.0.1:8000/django-admin/

احراز هویت: هدر `Authorization: Bearer <access_token>`

## Endpointها

| متد | مسیر | دسترسی | توضیح |
|---|---|---|---|
| POST | `/api/auth/register/` | همه | ثبت‌نام (همیشه Customer) |
| POST | `/api/auth/login/` | همه | دریافت `access` و `refresh` |
| POST | `/api/auth/refresh/` | همه | تمدید توکن (چرخش و blacklist) |
| POST | `/api/auth/logout/` | کاربر | body: `{"refresh": "..."}` |
| GET/PATCH | `/api/auth/profile/` | کاربر | پروفایل خود کاربر |
| GET | `/api/categories/` | همه | دسته‌بندی‌های فعال |
| GET | `/api/categories/{id}/products/` | همه | محصولات یک دسته |
| GET | `/api/products/` | همه | `?category=&search=&ordering=price&min_price=&max_price=&in_stock=true` |
| GET | `/api/products/{id}/` | همه | جزئیات محصول |
| GET | `/api/cart/` | Customer | مشاهده سبد و قیمت نهایی |
| POST | `/api/cart/items/` | Customer | `{"product_id": 1, "quantity": 2}` |
| PATCH | `/api/cart/items/{id}/` | Customer | `{"quantity": 3}` یا `{"delta": 1}` / `{"delta": -1}` |
| DELETE | `/api/cart/items/{id}/` | Customer | حذف آیتم |
| DELETE | `/api/cart/clear/` | Customer | خالی کردن سبد |
| POST | `/api/coupons/validate/` | Customer | پیش‌نمایش تخفیف روی سبد `{"code": "SUMMER20"}` |
| POST | `/api/orders/checkout/` | Customer | ثبت سفارش `{"coupon_code": "SUMMER20"}` (اختیاری) |
| GET | `/api/orders/`، `/api/orders/{id}/` | Customer | فقط سفارش‌های خود کاربر |
| GET/PATCH | `/api/admin/users/` | Admin | مشاهده، تغییر `role`، `is_active` |
| CRUD | `/api/admin/categories/` | Admin | مدیریت دسته‌بندی |
| CRUD | `/api/admin/products/` | Admin | مدیریت محصول (`stock`، `is_active` با PATCH) |
| CRUD | `/api/admin/coupons/` | Admin | مدیریت کد تخفیف |
| GET | `/api/admin/orders/`، `/api/admin/orders/{id}/` | Admin | همه سفارش‌ها (`?status=&user=&search=`) |
| PATCH | `/api/admin/orders/{id}/status/` | Admin | `{"status": "paid"}` |

## تصمیم‌های طراحی

- **Checkout اتمیک**: همه مراحل داخل `transaction.atomic()` و با `select_for_update()` روی محصولات (روی PostgreSQL قفل واقعی؛ SQLite فقط برای توسعه).
- **Snapshot سفارش**: `OrderItem` نام و قیمت محصول را هنگام خرید ذخیره می‌کند؛ تغییر یا حتی حذف محصول روی سفارش قبلی اثر ندارد.
- **کد تخفیف**: بررسی وجود، فعال بودن، انقضا، حداقل مبلغ و مصرف قبلی؛ قید یکتای `(user, coupon)` جلوی مصرف دوباره (حتی همزمان) را می‌گیرد. تخفیف هرگز از جمع کالاها بیشتر نمی‌شود.
- **وضعیت سفارش**: گذارهای مجاز `pending → paid → processing → shipped → delivered` و لغو از pending/paid/processing. لغو، موجودی را برمی‌گرداند و کد تخفیف را آزاد می‌کند.
- **محصول قابل فروش**: محصول و دسته‌بندی‌اش هر دو باید فعال باشند. محصول بدون موجودی نمایش داده می‌شود اما قابل افزودن به سبد نیست.
- **حذف دسته‌بندی** که محصول دارد (`PROTECT`) با خطای 409 رد می‌شود.
- **قالب خطا**: `{"success": false, "error": {"code", "message", "details"}}`
- **مبالغ** به‌صورت عدد صحیح (تومان) ذخیره می‌شوند؛ هزینه ارسال ثابت در `SHOP_SHIPPING_COST` (settings).
- **انتخاب View**: `ModelViewSet` برای CRUD ادمین، `ReadOnlyModelViewSet` برای بخش مشتری، `GenericAPIView`/generics برای Register و Profile، `APIView` برای Checkout، سبد و Logout.
