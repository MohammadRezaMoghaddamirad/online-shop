from email_validator import validate_email as check_email, EmailNotValidError
from rest_framework import serializers


def normalize_email(value: str) -> str:
    """اعتبارسنجی و نرمال‌سازی ایمیل (بدون چک DNS) و تبدیل به حروف کوچک"""
    try:
        value = check_email(value.strip(), check_deliverability=False).normalized
    except EmailNotValidError:
        raise serializers.ValidationError('ایمیل معتبر نیست.')
    return value.lower()
