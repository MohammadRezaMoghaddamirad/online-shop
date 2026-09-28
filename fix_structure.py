"""
اصلاح ساختار:
- urls/ (پوشه) → urls.py (فایل)
- ساخت services/ (اختیاری)
"""
import shutil
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


def fix_urls(app_path, app_name):
    """تبدیل urls/ پوشه به urls.py فایل"""
    urls_dir = app_path / "urls"
    urls_file = app_path / "urls.py"

    # اگر urls/ پوشه هست
    if urls_dir.exists() and urls_dir.is_dir():
        v1_file = urls_dir / "v1.py"

        if v1_file.exists():
            content = v1_file.read_text(encoding='utf-8')

            # اگر urls.py از قبل هست، بکاپ بگیر
            if urls_file.exists():
                urls_file.unlink()

            urls_file.write_text(content, encoding='utf-8')
            log(f"  ✅ urls/v1.py → urls.py", "green")

            shutil.rmtree(urls_dir)
            log(f"  ✅ پوشه urls/ حذف شد", "green")
        else:
            log(f"  ⚠️ v1.py در urls/ نیست", "yellow")

    # اگر urls.py از قبل هست
    elif urls_file.exists():
        log(f"  ✅ urls.py از قبل هست", "green")
    else:
        log(f"  ⚠️ نه urls/ نه urls.py", "yellow")


def create_services(app_path, app_name):
    """ساخت پوشه services/ اگر نیست"""
    services_dir = app_path / "services"

    if not services_dir.exists():
        services_dir.mkdir()
        (services_dir / "__init__.py").touch()
        log(f"  ✅ services/ ساخته شد", "green")
    else:
        log(f"  ✅ services/ از قبل هست", "green")


def main():
    log("\n" + "=" * 60, "cyan")
    log("  Fix structure: urls/ → urls.py", "cyan")
    log("=" * 60, "cyan")

    for app in APPS:
        app_path = APPS_DIR / app
        if not app_path.exists():
            log(f"\n⚠️ {app} پیدا نشد", "yellow")
            continue

        log(f"\n🔧 {app}", "cyan")
        fix_urls(app_path, app)
        create_services(app_path, app)

    log("\n" + "=" * 60, "cyan")
    log("  ✅ Fix complete!", "green")
    log("=" * 60, "cyan")
    log("\n⚠️ حالا config/urls.py را به‌روز کنید:", "yellow")
    log("  بدون .v1 در انتها:", "white")
    log("  path('products/', include('apps.products.urls')),", "white")


if __name__ == "__main__":
    main()