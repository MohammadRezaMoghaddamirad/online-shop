"""
تست Checkout (مهم‌ترین بخش پروژه)
"""
import pytest
from apps.products.models import Product


@pytest.mark.django_db
class TestCheckout:
    """تست ثبت سفارش"""

    cart_add_url = '/api/v1/carts/add/'
    checkout_url = '/api/v1/orders/checkout/'

    def test_checkout_success(self, customer_client, product, coupon):
        """Checkout موفق با کد تخفیف"""
        customer_client.post(self.cart_add_url, {
            'product_id': product.id,
            'quantity': 2
        })

        response = customer_client.post(self.checkout_url, {
            'coupon_code': coupon.code,
            'shipping_cost': 50000
        })

        assert response.status_code == 201
        data = response.data
        assert data['subtotal'] == '100000000'
        assert data['discount_amount'] == '20000000'
        assert data['total_amount'] == '80050000'
        assert data['status'] == 'pending'

    def test_checkout_empty_cart(self, customer_client):
        """Checkout با سبد خالی"""
        response = customer_client.post(self.checkout_url, {
            'shipping_cost': 50000
        })

        assert response.status_code == 400


    def test_checkout_reduces_stock(self, customer_client, product):
        """کاهش موجودی بعد از Checkout"""
        initial_stock = product.stock

        customer_client.post(self.cart_add_url, {
            'product_id': product.id,
            'quantity': 3
        })

        customer_client.post(self.checkout_url, {
            'shipping_cost': 50000
        })

        product.refresh_from_db()
        assert product.stock == initial_stock - 3

    def test_checkout_clears_cart(self, customer_client, product):
        """سبد بعد از Checkout خالی می‌شود"""
        customer_client.post(self.cart_add_url, {
            'product_id': product.id,
            'quantity': 1
        })

        customer_client.post(self.checkout_url, {
            'shipping_cost': 50000
        })

        response = customer_client.get('/api/v1/carts/')
        assert response.data['items'] == []


@pytest.mark.django_db
class TestAdminOrders:
    """تست سفارش‌های ادمین"""

    def test_admin_can_see_all_orders(self, admin_client, customer_client, product):
        """ادمین همه سفارش‌ها را می‌بیند"""
        customer_client.post('/api/v1/carts/add/', {
            'product_id': product.id,
            'quantity': 1
        })
        customer_client.post('/api/v1/orders/checkout/', {
            'shipping_cost': 50000
        })

        response = admin_client.get('/api/v1/orders/admin/')

        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_customer_cannot_see_admin_orders(self, customer_client):
        """کاربر عادی به سفارش‌های ادمین دسترسی ندارد"""
        response = customer_client.get('/api/v1/orders/admin/')

        assert response.status_code == 403