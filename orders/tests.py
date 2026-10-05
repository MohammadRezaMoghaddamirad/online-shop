from datetime import timedelta

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from catalog.models import Category, Product
from coupons.models import Coupon
from orders.models import Order
from users.models import User

PASSWORD = "Str0ng-Pass!234"


@override_settings(SHOP_SHIPPING_COST=50_000)
class ShopFlowTests(APITestCase):
    def setUp(self):
        self.ali = User.objects.create_user("ali", "ali@example.com", PASSWORD)
        self.sara = User.objects.create_user("sara", "sara@example.com", PASSWORD)
        self.boss = User.objects.create_user("boss", "boss@example.com", PASSWORD, role=User.Role.ADMIN)
        self.category = Category.objects.create(name="Mobile")
        self.iphone = Product.objects.create(name="iPhone", price=50_000_000, category=self.category, stock=10)
        self.coupon = Coupon.objects.create(
            code="SUMMER20",
            discount_type=Coupon.DiscountType.PERCENT,
            value=20,
            min_order_amount=1_000_000,
            expires_at=timezone.now() + timedelta(days=5),
        )

    def add_to_cart(self, product, quantity):
        return self.client.post("/api/cart/items/", {"product_id": product.id, "quantity": quantity}, format="json")

    # ---------- auth ----------
    def test_register_login_and_logout(self):
        payload = {
            "username": "new", "email": "new@example.com",
            "password": PASSWORD, "password_confirm": PASSWORD,
        }
        self.assertEqual(self.client.post("/api/auth/register/", payload, format="json").status_code, 201)
        login = self.client.post("/api/auth/login/", {"username": "new", "password": PASSWORD}, format="json")
        self.assertEqual(login.status_code, 200)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        self.assertEqual(self.client.get("/api/auth/profile/").data["role"], "customer")
        out = self.client.post("/api/auth/logout/", {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(out.status_code, 204)
        again = self.client.post("/api/auth/refresh/", {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(again.status_code, 401)

    # ---------- cart ----------
    def test_cart_requires_login_and_respects_stock(self):
        self.assertEqual(self.client.get("/api/cart/").status_code, 401)
        self.client.force_authenticate(self.ali)
        self.assertEqual(self.add_to_cart(self.iphone, 11).status_code, 400)
        response = self.add_to_cart(self.iphone, 2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total_price"], 100_000_000)

    def test_cart_item_increase_decrease(self):
        self.client.force_authenticate(self.ali)
        cart = self.add_to_cart(self.iphone, 1).data
        item_id = cart["items"][0]["id"]
        up = self.client.patch(f"/api/cart/items/{item_id}/", {"delta": 2}, format="json")
        self.assertEqual(up.data["items"][0]["quantity"], 3)
        down = self.client.patch(f"/api/cart/items/{item_id}/", {"delta": -1}, format="json")
        self.assertEqual(down.data["items"][0]["quantity"], 2)
        # کاربر دیگر به آیتم ما دسترسی ندارد
        self.client.force_authenticate(self.sara)
        self.assertEqual(self.client.delete(f"/api/cart/items/{item_id}/").status_code, 404)

    # ---------- checkout ----------
    def test_checkout_with_coupon_snapshot_and_stock(self):
        self.client.force_authenticate(self.ali)
        self.add_to_cart(self.iphone, 3)
        response = self.client.post("/api/orders/checkout/", {"coupon_code": "summer20"}, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["subtotal"], 150_000_000)
        self.assertEqual(response.data["discount_amount"], 30_000_000)
        self.assertEqual(response.data["shipping_cost"], 50_000)
        self.assertEqual(response.data["total"], 120_050_000)

        self.iphone.refresh_from_db()
        self.assertEqual(self.iphone.stock, 7)
        self.assertEqual(self.client.get("/api/cart/").data["items"], [])

        # تغییر قیمت محصول روی سفارش قبلی اثری ندارد
        self.iphone.price = 1
        self.iphone.name = "Changed"
        self.iphone.save()
        detail = self.client.get(f"/api/orders/{response.data['id']}/").data
        self.assertEqual(detail["items"][0]["unit_price"], 50_000_000)
        self.assertEqual(detail["items"][0]["product_name"], "iPhone")

        # مصرف دوباره‌ی کد تخفیف ممکن نیست
        self.iphone.price = 50_000_000
        self.iphone.save()
        self.add_to_cart(self.iphone, 1)
        again = self.client.post("/api/orders/checkout/", {"coupon_code": "SUMMER20"}, format="json")
        self.assertEqual(again.status_code, 400)

    def test_checkout_empty_cart_fails(self):
        self.client.force_authenticate(self.ali)
        self.assertEqual(self.client.post("/api/orders/checkout/", {}, format="json").status_code, 400)

    def test_out_of_stock_cannot_be_bought(self):
        self.iphone.stock = 0
        self.iphone.save()
        self.client.force_authenticate(self.ali)
        self.assertEqual(self.add_to_cart(self.iphone, 1).status_code, 400)

    # ---------- visibility & permissions ----------
    def test_inactive_product_hidden(self):
        hidden = Product.objects.create(name="Hidden", price=10, category=self.category, stock=1, is_active=False)
        response = self.client.get("/api/products/")
        names = [p["name"] for p in response.data["results"]]
        self.assertIn("iPhone", names)
        self.assertNotIn("Hidden", names)
        self.assertEqual(self.client.get(f"/api/products/{hidden.id}/").status_code, 404)

    def test_product_search_filter_ordering(self):
        Product.objects.create(name="Galaxy", price=30_000_000, category=self.category, stock=5)
        response = self.client.get("/api/products/?search=gal")
        self.assertEqual(response.data["count"], 1)
        response = self.client.get("/api/products/?ordering=price")
        self.assertEqual(response.data["results"][0]["name"], "Galaxy")

    def test_only_admin_manages_products(self):
        payload = {"name": "Pixel", "price": 20_000_000, "category": self.category.id, "stock": 4}
        self.client.force_authenticate(self.ali)
        self.assertEqual(self.client.post("/api/admin/products/", payload, format="json").status_code, 403)
        self.client.force_authenticate(self.boss)
        self.assertEqual(self.client.post("/api/admin/products/", payload, format="json").status_code, 201)

    def test_customer_sees_only_own_orders(self):
        self.client.force_authenticate(self.ali)
        self.add_to_cart(self.iphone, 1)
        order_id = self.client.post("/api/orders/checkout/", {}, format="json").data["id"]
        self.client.force_authenticate(self.sara)
        self.assertEqual(self.client.get("/api/orders/").data["count"], 0)
        self.assertEqual(self.client.get(f"/api/orders/{order_id}/").status_code, 404)

    # ---------- admin order flow ----------
    def test_admin_cancel_restores_stock_and_coupon(self):
        self.client.force_authenticate(self.ali)
        self.add_to_cart(self.iphone, 2)
        order_id = self.client.post("/api/orders/checkout/", {"coupon_code": "SUMMER20"}, format="json").data["id"]

        self.client.force_authenticate(self.boss)
        bad = self.client.patch(f"/api/admin/orders/{order_id}/status/", {"status": "delivered"}, format="json")
        self.assertEqual(bad.status_code, 400)
        ok = self.client.patch(f"/api/admin/orders/{order_id}/status/", {"status": "cancelled"}, format="json")
        self.assertEqual(ok.status_code, 200)

        self.iphone.refresh_from_db()
        self.assertEqual(self.iphone.stock, 10)
        self.assertEqual(Order.objects.get(pk=order_id).status, "cancelled")
        self.assertFalse(self.coupon.usages.exists())

    def test_admin_cannot_demote_self(self):
        self.client.force_authenticate(self.boss)
        response = self.client.patch(f"/api/admin/users/{self.boss.id}/", {"role": "customer"}, format="json")
        self.assertEqual(response.status_code, 400)
