"""
تبدیل importهای نسبی به مطلق — نسخه نهایی (بعد از گروه‌بندی)
"""
import re
from pathlib import Path

APPS_DIR = Path("apps").resolve()


def log(msg, color="white"):
    colors = {
        "white": "\033[97m",
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, '')}{msg}{colors['end']}")


def get_app_name(file_path):
    parts = file_path.parts
    for i, part in enumerate(parts):
        if part == 'apps' and i + 1 < len(parts):
            return parts[i + 1]
    return None


def fix_file(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        app_name = get_app_name(file_path)
        if not app_name:
            return False

        # serializers
        content = re.sub(r'from \.\.\.\.\.\.serializers', f'from apps.{app_name}.api.v1.serializers', content)
        content = re.sub(r'from \.\.\.\.\.serializers', f'from apps.{app_name}.api.v1.serializers', content)
        content = re.sub(r'from \.\.\.\.serializers', f'from apps.{app_name}.api.v1.serializers', content)
        content = re.sub(r'from \.\.\.serializers', f'from apps.{app_name}.api.v1.serializers', content)
        content = re.sub(r'from \.\.serializers', f'from apps.{app_name}.api.v1.serializers', content)
        content = re.sub(r'from \.serializers', f'from apps.{app_name}.api.v1.serializers', content)

        # permissions
        content = re.sub(r'from \.\.\.\.\.permissions', f'from apps.{app_name}.api.v1.permissions', content)
        content = re.sub(r'from \.\.\.\.permissions', f'from apps.{app_name}.api.v1.permissions', content)
        content = re.sub(r'from \.\.\.permissions', f'from apps.{app_name}.api.v1.permissions', content)
        content = re.sub(r'from \.\.permissions', f'from apps.{app_name}.api.v1.permissions', content)

        # services
        content = re.sub(r'from \.\.\.\.\.\.services', f'from apps.{app_name}.services', content)
        content = re.sub(r'from \.\.\.\.\.services', f'from apps.{app_name}.services', content)
        content = re.sub(r'from \.\.\.\.services', f'from apps.{app_name}.services', content)
        content = re.sub(r'from \.\.\.services', f'from apps.{app_name}.services', content)

        # utils
        content = re.sub(r'from \.\.\.\.\.\.utils', f'from apps.{app_name}.utils', content)
        content = re.sub(r'from \.\.\.\.\.utils', f'from apps.{app_name}.utils', content)
        content = re.sub(r'from \.\.\.\.utils', f'from apps.{app_name}.utils', content)
        content = re.sub(r'from \.\.\.utils', f'from apps.{app_name}.utils', content)

        # models
        content = re.sub(r'from \.\.\.\.\.\.models', f'from apps.{app_name}.models', content)
        content = re.sub(r'from \.\.\.\.\.models', f'from apps.{app_name}.models', content)
        content = re.sub(r'from \.\.\.\.models', f'from apps.{app_name}.models', content)
        content = re.sub(r'from \.\.\.models', f'from apps.{app_name}.models', content)

        # views (در urls.py یا __init__.py)
        content = re.sub(r'from \.views', f'from apps.{app_name}.api.v1.views', content)

        # auth (در views/__init__.py)
        content = re.sub(r'from \.auth', f'from apps.{app_name}.api.v1.views.auth', content)

        # customer
        content = re.sub(r'from \.customer\.order_viewset', f'from apps.{app_name}.api.v1.views.customer.order_viewset', content)
        content = re.sub(r'from \.admin_order_viewset', f'from apps.{app_name}.api.v1.views.admin_order_viewset', content)

        # register/login/logout (در views/auth/__init__.py)
        content = re.sub(r'from \.register', f'from apps.{app_name}.api.v1.views.auth.register', content)
        content = re.sub(r'from \.login', f'from apps.{app_name}.api.v1.views.auth.login', content)
        content = re.sub(r'from \.logout', f'from apps.{app_name}.api.v1.views.auth.logout', content)

        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"  ⚠️ خطا در {file_path}: {e}")
        return False


def main():
    log("\n" + "=" * 60, "cyan")
    log("  تبدیل همه importهای نسبی به مطلق", "cyan")
    log("=" * 60, "cyan")

    count = 0
    for py_file in APPS_DIR.rglob("api/**/*.py"):
        if "__pycache__" in str(py_file):
            continue
        if fix_file(py_file):
            log(f"  ✅ {py_file.relative_to(APPS_DIR)}", "green")
            count += 1

    log("\n" + "=" * 60, "cyan")
    log(f"  ✅ {count} فایل اصلاح شد", "green")
    log("=" * 60, "cyan")


if __name__ == "__main__":
    main()