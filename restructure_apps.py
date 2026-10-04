"""
یکسان‌سازی ساختار همه اپ‌ها
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


def ensure_dir(path):
    """ساخت پوشه اگر نیست"""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return True
    return False


def ensure_init(path):
    """ساخت __init__.py اگر نیست"""
    if not path.exists():
        path.touch()
        return True
    return False


def restructure_app(app_name):
    log(f"\n🔧 Processing {app_name}...", "cyan")

    app_path = APPS_DIR / app_name
    if not app_path.exists():
        log(f"  ⚠️ پیدا نشد", "yellow")
        return

    # ۱. services/
    services_path = app_path / "services"
    if ensure_dir(services_path):
        log(f"  ✅ services/ ساخته شد", "green")
    ensure_init(services_path / "__init__.py")

    # ۲. utils/
    utils_path = app_path / "utils"
    if ensure_dir(utils_path):
        log(f"  ✅ utils/ ساخته شد", "green")
    ensure_init(utils_path / "__init__.py")

    # ۳. tests/
    tests_path = app_path / "tests"
    if ensure_dir(tests_path):
        log(f"  ✅ tests/ ساخته شد", "green")
    ensure_init(tests_path / "__init__.py")

    # ۴. api/__init__.py
    api_path = app_path / "api"
    if ensure_dir(api_path):
        log(f"  ✅ api/ ساخته شد", "green")
    ensure_init(api_path / "__init__.py")

    # ۵. api/v1/__init__.py
    api_v1_path = app_path / "api" / "v1"
    if ensure_dir(api_v1_path):
        log(f"  ✅ api/v1/ ساخته شد", "green")
    ensure_init(api_v1_path / "__init__.py")


def main():
    log("\n" + "=" * 60, "cyan")
    log("  یکسان‌سازی ساختار همه اپ‌ها", "cyan")
    log("=" * 60, "cyan")

    for app in APPS:
        restructure_app(app)

    log("\n" + "=" * 60, "cyan")
    log("  ✅ تمام!", "green")
    log("=" * 60, "cyan")


if __name__ == "__main__":
    main()