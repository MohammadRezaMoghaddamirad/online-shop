"""
بررسی وضعیت دیتابیس
"""
import os
import sys
import django
from pathlib import Path

# اضافه کردن ریشه پروژه به sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.categories.models import Category
from apps.orders.models import Order
from apps.carts.models import Cart

User = get_user_model()

print("=" * 50)
print("  Database Status")
print("=" * 50)
print(f"Users:      {User.objects.count()}")
print(f"Usernames:  {list(User.objects.values_list('username', flat=True))}")
print(f"Products:   {Product.objects.count()}")
print(f"Categories: {Category.objects.count()}")
print(f"Orders:     {Order.objects.count()}")
print(f"Carts:      {Cart.objects.count()}")
print("=" * 50)