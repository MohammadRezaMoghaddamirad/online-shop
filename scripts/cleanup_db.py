"""
پاکسازی کاربران تستی از دیتابیس اصلی
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

TEST_USERNAMES = [
    'testuser',
    'ali',
    'finaltest',
    'brunotest',
    'autotest_1790413554',
    'autotest_1790413768',
    'autotest_1790415044',
    'autotest_1790678557',
]

print("=" * 50)
print("  پاکسازی کاربران تستی")
print("=" * 50)

for username in TEST_USERNAMES:
    try:
        user = User.objects.get(username=username)
        user.delete()
        print(f"✅ حذف شد: {username}")
    except User.DoesNotExist:
        print(f"⚪ پیدا نشد: {username}")

print("=" * 50)
print(f"  کاربران باقیمانده: {list(User.objects.values_list('username', flat=True))}")
print("=" * 50)