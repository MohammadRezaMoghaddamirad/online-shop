"""
تست کامل همه endpointهای فروشگاه آنلاین
"""
import requests
import json
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://127.0.0.1:8000/api/v1"
ADMIN_USER = "admin"
ADMIN_PASS = "admin1234"
CUSTOMER_USER = "reza"
CUSTOMER_PASS = "Reza@12345"

# نتایج تست‌ها
results = []
admin_token = None
customer_token = None
customer_refresh = None
created_category_id = None
created_product_id = None
created_coupon_id = None
created_coupon_code = None
created_cart_item_id = None
created_order_id = None


def log(msg, color=Fore.WHITE):
    print(f"{color}{msg}{Style.RESET_ALL}")


def test(name, method, endpoint, expected_code, data=None, token=None, params=None):
    """اجرای یک تست"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PATCH":
            resp = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)

        success = resp.status_code == expected_code
        results.append((name, method, endpoint, expected_code, resp.status_code, success))

        if success:
            log(f"  ✅ {name} ({method} {endpoint}) → {resp.status_code}", Fore.GREEN)
        else:
            log(f"  ❌ {name} ({method} {endpoint}) → {resp.status_code} (انتظار: {expected_code})", Fore.RED)
            log(f"     Response: {resp.text[:200]}", Fore.YELLOW)

        return resp
    except Exception as e:
        log(f"  💥 {name} → خطا: {e}", Fore.RED)
        results.append((name, method, endpoint, expected_code, "ERROR", False))
        return None


# ============================================
# شروع تست‌ها
# ============================================

log("\n" + "=" * 60, Fore.CYAN)
log("  شروع تست کامل endpointها", Fore.CYAN)
log("=" * 60 + "\n", Fore.CYAN)

# ---------- ۰. آماده‌سازی: پاک کردن سبد کاربر ----------
log("📌 مرحله ۰: آماده‌سازی", Fore.CYAN)

# اول Login با کاربر تست تا سبدش را خالی کنیم
r = requests.post(
    f"{BASE_URL}/auth/login/",
    json={"username": CUSTOMER_USER, "password": CUSTOMER_PASS},
    timeout=10
)
if r.status_code == 200:
    temp_token = r.json().get("access")
    # خالی کردن سبد
    requests.delete(
        f"{BASE_URL}/carts/clear/",
        headers={"Authorization": f"Bearer {temp_token}"},
        timeout=10
    )
    log(f"  ✅ سبد کاربر {CUSTOMER_USER} خالی شد", Fore.GREEN)
else:
    log(f"  ⚠️ کاربر {CUSTOMER_USER} پیدا نشد", Fore.YELLOW)

# ---------- ۱. احراز هویت ----------
log("\n📌 مرحله ۱: احراز هویت", Fore.CYAN)

# ۱. ثبت‌نام
test(
    "ثبت‌نام کاربر جدید",
    "POST", "/auth/register/", 201,
    {
        "username": f"autotest_{int(datetime.now().timestamp())}",
        "email": f"autotest_{int(datetime.now().timestamp())}@test.com",
        "password": "Test@12345",
        "password2": "Test@12345",
        "phone": "09121111111",
        "address": "Test Address"
    }
)

# ۲. ورود ادمین
r = test(
    "ورود ادمین",
    "POST", "/auth/login/", 200,
    {"username": ADMIN_USER, "password": ADMIN_PASS}
)
if r and r.status_code == 200:
    admin_token = r.json().get("access")

# ۳. ورود کاربر (reza)
r = test(
    "ورود کاربر",
    "POST", "/auth/login/", 200,
    {"username": CUSTOMER_USER, "password": CUSTOMER_PASS}
)
if r and r.status_code == 200:
    data = r.json()
    customer_token = data.get("access")
    customer_refresh = data.get("refresh")

# ---------- ۲. پروفایل ----------
log("\n📌 مرحله ۲: پروفایل کاربر", Fore.CYAN)

test("مشاهده پروفایل", "GET", "/accounts/profile/", 200, token=customer_token)

test("ویرایش پروفایل", "PATCH", "/accounts/profile/", 200,
     {"phone": "09999999999", "address": "Isfahan"},
     token=customer_token)

test("لیست کاربران (ادمین)", "GET", "/accounts/users/", 200, token=admin_token)

# ---------- ۳. دسته‌بندی‌ها ----------
log("\n📌 مرحله ۳: دسته‌بندی‌ها", Fore.CYAN)

test("لیست دسته‌بندی‌ها", "GET", "/categories/", 200)

# ساخت دسته جدید
r = test("ساخت دسته‌بندی", "POST", "/categories/", 201,
         {
             "name": f"تست_{int(datetime.now().timestamp())}",
             "description": "دسته تست",
             "is_active": True
         },
         token=admin_token)
if r and r.status_code == 201:
    created_category_id = r.json().get("id")

if created_category_id:
    test("جزئیات دسته", "GET", f"/categories/{created_category_id}/", 200)
    test("ویرایش دسته", "PATCH", f"/categories/{created_category_id}/", 200,
         {"description": "ویرایش شده"}, token=admin_token)

# ---------- ۴. محصولات ----------
log("\n📌 مرحله ۴: محصولات", Fore.CYAN)

test("لیست محصولات", "GET", "/products/", 200)

# ساخت محصول
r = test("ساخت محصول", "POST", "/products/", 201,
         {
             "name": f"محصول تست {int(datetime.now().timestamp())}",
             "description": "تست",
             "price": 50000000,
             "category_id": created_category_id or 1,
             "stock": 10,
             "is_active": True
         },
         token=admin_token)
if r and r.status_code == 201:
    created_product_id = r.json().get("id")

if created_product_id:
    test("جزئیات محصول", "GET", f"/products/{created_product_id}/", 200)
    test("ویرایش محصول", "PATCH", f"/products/{created_product_id}/", 200,
         {"price": 45000000}, token=admin_token)
    test("ویرایش موجودی", "PATCH", f"/products/{created_product_id}/stock/", 200,
         {"stock": 20}, token=admin_token)

test("جستجو و مرتب‌سازی", "GET", "/products/?ordering=-price", 200)

# ---------- ۵. سبد خرید ----------
log("\n📌 مرحله ۵: سبد خرید", Fore.CYAN)

test("مشاهده سبد", "GET", "/carts/", 200, token=customer_token)

# افزودن محصول به سبد
r = test("افزودن به سبد", "POST", "/carts/add/", 200,
         {"product_id": created_product_id or 1, "quantity": 2},
         token=customer_token)

if r and r.status_code == 200:
    items = r.json().get("items", [])
    if items:
        created_cart_item_id = items[0].get("id")

if created_cart_item_id:
    test("تغییر تعداد", "PATCH", f"/carts/items/{created_cart_item_id}/", 200,
         {"quantity": 3}, token=customer_token)

# ---------- ۶. کدهای تخفیف ----------
log("\n📌 مرحله ۶: کدهای تخفیف", Fore.CYAN)

test("لیست کدها", "GET", "/coupons/", 200, token=admin_token)

# ساخت کد تخفیف جدید (اختصاصی برای این تست)
created_coupon_code = f"TEST{int(datetime.now().timestamp()) % 1000000}"

r = test("ساخت کد تخفیف", "POST", "/coupons/", 201,
         {
             "code": created_coupon_code,
             "discount_type": "percent",
             "discount_value": 15,
             "min_order_amount": 100000,
             "expires_at": (datetime.now() + timedelta(days=30)).isoformat() + "Z",
             "is_active": True
         },
         token=admin_token)
if r and r.status_code == 201:
    created_coupon_id = r.json().get("id")

if created_coupon_id:
    test("جزئیات کد", "GET", f"/coupons/{created_coupon_id}/", 200, token=admin_token)
    test("ویرایش کد", "PATCH", f"/coupons/{created_coupon_id}/", 200,
         {"discount_value": 20}, token=admin_token)

# ---------- ۷. سفارش‌ها ----------
log("\n📌 مرحله ۷: سفارش‌ها", Fore.CYAN)

# Checkout با کد تخفیف جدید (که کاربر reza هنوز استفاده نکرده)
r = test("ثبت سفارش (Checkout)", "POST", "/orders/checkout/", 201,
         {"coupon_code": created_coupon_code, "shipping_cost": 50000},
         token=customer_token)
if r and r.status_code == 201:
    created_order_id = r.json().get("id")

test("سفارش‌های من", "GET", "/orders/", 200, token=customer_token)

if created_order_id:
    test("جزئیات سفارش", "GET", f"/orders/{created_order_id}/", 200, token=customer_token)

test("سفارش‌های ادمین", "GET", "/orders/admin/", 200, token=admin_token)

if created_order_id:
    test("تغییر وضعیت سفارش", "PATCH",
         f"/orders/admin/{created_order_id}/status/", 200,
         {"status": "paid"}, token=admin_token)

# ---------- ۸. پاکسازی ----------
log("\n📌 مرحله ۸: پاکسازی", Fore.CYAN)

if created_coupon_id:
    test("حذف کد تخفیف", "DELETE", f"/coupons/{created_coupon_id}/", 204, token=admin_token)

if created_product_id:
    test("حذف محصول", "DELETE", f"/products/{created_product_id}/", 204, token=admin_token)

if created_category_id:
    test("حذف دسته", "DELETE", f"/categories/{created_category_id}/", 204, token=admin_token)

# ---------- خلاصه ----------
log("\n" + "=" * 60, Fore.CYAN)
log("  خلاصه نتایج", Fore.CYAN)
log("=" * 60, Fore.CYAN)

passed = sum(1 for r in results if r[5])
failed = len(results) - passed
total = len(results)

log(f"\n  ✅ موفق: {passed}/{total}", Fore.GREEN if passed == total else Fore.YELLOW)
log(f"  ❌ ناموفق: {failed}/{total}", Fore.RED if failed > 0 else Fore.GREEN)
log(f"  📊 درصد موفقیت: {int(passed / total * 100)}%\n", Fore.CYAN)

if failed > 0:
    log("  لیست تست‌های ناموفق:", Fore.RED)
    for name, method, endpoint, expected, actual, success in results:
        if not success:
            log(f"    ❌ {name}: {method} {endpoint} → {actual} (انتظار {expected})", Fore.RED)

log("\n" + "=" * 60 + "\n", Fore.CYAN)