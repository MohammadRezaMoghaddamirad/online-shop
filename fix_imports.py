"""
اصلاح importها: ..views → .views در فایل‌های urls.py
"""
from pathlib import Path

APPS_DIR = Path("apps").resolve()
APPS = ['authentication', 'accounts', 'categories', 'products', 'carts', 'coupons', 'orders']


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


def fix_urls_file(urls_file):
    """اصلاح ..views → .views"""
    if not urls_file.exists():
        return False

    content = urls_file.read_text(encoding='utf-8')
    original = content

    # تغییر ..views → .views
    content = content.replace('from ..views', 'from .views')
    content = content.replace('from ..permissions', 'from .permissions')
    content = content.replace('from ..serializers', 'from .serializers')
    content = content.replace('from ..models', 'from .models')
    content = content.replace('from ..services', 'from .services')

    if content != original:
        urls_file.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    log("\n" + "=" * 60, "cyan")
    log("  Fix imports: ..views → .views", "cyan")
    log("=" * 60, "cyan")

    count = 0
    for app in APPS:
        urls_file = APPS_DIR / app / "urls.py"

        if urls_file.exists():
            if fix_urls_file(urls_file):
                log(f"  ✅ apps/{app}/urls.py — اصلاح شد", "green")
                count += 1
            else:
                log(f"  ⚪ apps/{app}/urls.py — تغییری لازم نبود", "white")
        else:
            log(f"  ⚠️ apps/{app}/urls.py — پیدا نشد", "yellow")

    log("\n" + "=" * 60, "cyan")
    log(f"  ✅ {count} فایل اصلاح شد", "green")
    log("=" * 60, "cyan")


if __name__ == "__main__":
    main()