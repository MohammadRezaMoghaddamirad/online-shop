from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _body(code, message, details=None):
    return {"success": False, "error": {"code": code, "message": message, "details": details}}


def custom_exception_handler(exc, context):
    """فرمت یکسان برای همه خطاها:

    {"success": false, "error": {"code": "...", "message": "...", "details": ...}}
    """
    if isinstance(exc, ProtectedError):
        return Response(
            _body("protected", "این مورد به داده‌های دیگر وابسته است و قابل حذف نیست."),
            status=status.HTTP_409_CONFLICT,
        )

    response = exception_handler(exc, context)
    if response is None:  # خطای ۵۰۰ را به Django می‌سپاریم
        return None

    data = response.data
    if isinstance(exc, ValidationError):
        response.data = _body("validation_error", "داده‌های ارسالی معتبر نیستند.", data)
        return response

    if isinstance(data, dict) and "detail" in data:
        message = str(data["detail"])
    else:
        message = str(data)
    code = getattr(exc, "default_code", "error")
    response.data = _body(code, message)
    return response


class BusinessRuleError(APIException):
    """خطای مربوط به قوانین کسب‌وکار"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'خطا در قوانین کسب‌وکار.'
    default_code = 'business_rule_error'