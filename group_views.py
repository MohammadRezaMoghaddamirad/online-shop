"""
گروه‌بندی views در پوشه‌های منطقی
"""
import shutil
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


def group_authentication_views():
    """گروه‌بندی views در authentication/api/v1/views/auth/"""
    log("\n🔧 Grouping authentication/views...", "cyan")

    views_path = APPS_DIR / "authentication" / "api" / "v1" / "views"
    auth_dir = views_path / "auth"

    auth_dir.mkdir(exist_ok=True)

    # انتقال فایل‌ها
    for file_name in ['register.py', 'login.py', 'logout.py']:
        src = views_path / file_name
        dst = auth_dir / file_name

        if src.exists():
            shutil.move(str(src), str(dst))
            log(f"  ✅ {file_name} → auth/{file_name}", "green")
        else:
            log(f"  ⚪ {file_name} پیدا نشد", "yellow")

    # auth/__init__.py
    (auth_dir / "__init__.py").write_text(
        "from .register import RegisterView\n"
        "from .login import LoginView\n"
        "from .logout import LogoutView\n\n"
        "__all__ = ['RegisterView', 'LoginView', 'LogoutView']\n",
        encoding='utf-8'
    )
    log(f"  ✅ auth/__init__.py ساخته شد", "green")

    # views/__init__.py
    (views_path / "__init__.py").write_text(
        "from .auth import RegisterView, LoginView, LogoutView\n\n"
        "__all__ = ['RegisterView', 'LoginView', 'LogoutView']\n",
        encoding='utf-8'
    )
    log(f"  ✅ views/__init__.py به‌روز شد", "green")


def group_orders_views():
    """گروه‌بندی views در orders/api/v1/views/"""
    log("\n🔧 Grouping orders/views...", "cyan")

    views_path = APPS_DIR / "orders" / "api" / "v1" / "views"

    customer_dir = views_path / "customer"
    customer_dir.mkdir(exist_ok=True)

    # انتقال order_viewset.py
    src = views_path / "order_viewset.py"
    dst = customer_dir / "order_viewset.py"

    if src.exists():
        shutil.move(str(src), str(dst))
        log(f"  ✅ order_viewset.py → customer/order_viewset.py", "green")

    # customer/__init__.py
    (customer_dir / "__init__.py").write_text(
        "from .order_viewset import OrderViewSet\n\n"
        "__all__ = ['OrderViewSet']\n",
        encoding='utf-8'
    )
    log(f"  ✅ customer/__init__.py ساخته شد", "green")

    # views/__init__.py
    (views_path / "__init__.py").write_text(
        "from .customer.order_viewset import OrderViewSet\n"
        "from .admin_order_viewset import AdminOrderViewSet\n\n"
        "__all__ = ['OrderViewSet', 'AdminOrderViewSet']\n",
        encoding='utf-8'
    )
    log(f"  ✅ views/__init__.py به‌روز شد", "green")


def main():
    log("\n" + "=" * 60, "cyan")
    log("  Grouping views into logical folders", "cyan")
    log("=" * 60, "cyan")

    group_authentication_views()
    group_orders_views()

    log("\n" + "=" * 60, "cyan")
    log("  ✅ Grouping complete!", "green")
    log("=" * 60, "cyan")


if __name__ == "__main__":
    main()