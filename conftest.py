"""
Pytest Fixtures برای پروژه فروشگاه آنلاین
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.products.models import Product
from apps.coupons.models import Coupon
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


# ============ API Client ============
@pytest.fixture
def api_client():
    """کلاینت API برای تست"""
    return APIClient()


# ============ Users ============
@pytest.fixture
def admin_user(db):
    """کاربر ادمین"""
    return User.objects.create_user(
        username='test_admin',
        email='admin@test.com',
        password='Admin@1234',
        role='admin'
    )


@pytest.fixture
def customer_user(db):
    """کاربر عادی"""
    return User.objects.create_user(
        username='test_customer',
        email='customer@test.com',
        password='Customer@1234',
        role='customer'
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    """کلاینت لاگین‌شده با ادمین"""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def customer_client(api_client, customer_user):
    """کلاینت لاگین‌شده با کاربر عادی"""
    api_client.force_authenticate(user=customer_user)
    return api_client


# ============ Categories ============
@pytest.fixture
def category(db):
    """دسته‌بندی نمونه"""
    return Category.objects.create(
        name='موبایل',
        description='گوشی‌های موبایل',
        is_active=True
    )


# ============ Products ============
@pytest.fixture
def product(db, category):
    """محصول نمونه"""
    return Product.objects.create(
        name='iPhone 15',
        description='آخرین مدل اپل',
        price=50000000,
        category=category,
        stock=10,
        is_active=True
    )


# ============ Coupons ============
@pytest.fixture
def coupon(db):
    """کد تخفیف نمونه"""
    return Coupon.objects.create(
        code='TEST20',
        discount_type='percent',
        discount_value=20,
        min_order_amount=100000,
        expires_at=timezone.now() + timedelta(days=30),
        is_active=True
    )