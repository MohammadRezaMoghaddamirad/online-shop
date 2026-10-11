import os
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ======== Security ========
def _env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def _env_list(name, default=''):
    return [v.strip() for v in os.environ.get(name, default).split(',') if v.strip()]


DEBUG = _env_bool('DEBUG', True)

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-only-key-change-in-production'
    else:
        raise ImproperlyConfigured('SECRET_KEY must be set when DEBUG=False')

ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS', '*' if DEBUG else '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'corsheaders',

    # Local apps
    'apps.accounts',
    'apps.authentication',
    'apps.categories',
    'apps.brands',
    'apps.banners',
    'apps.products',
    'apps.carts',
    'apps.coupons',
    'apps.orders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ======== PostgreSQL ========
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'shop_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# ======== Custom User ========
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ======== i18n ========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# ======== Static & Media ========
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======== DRF ========
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# ======== Simple JWT ========
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 30))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
# ======== drf-spectacular ========
SPECTACULAR_SETTINGS = {
    'TITLE': 'Online Shop API',
    'DESCRIPTION': 'API فروشگاه آنلاین',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # مسیرها با پیشوند کامل /api/v1/ نمایش داده می‌شوند (trim حذف شد)
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'SCHEMA_PATH_PREFIX_TRIM': False,

    'TAGS': [
        {'name': 'Auth',       'description': 'احراز هویت و ورود'},
        {'name': 'Profile',    'description': 'پروفایل کاربر جاری'},
        {'name': 'Users',      'description': 'مدیریت کاربران'},
        {'name': 'Categories', 'description': 'دسته‌بندی محصولات'},
        {'name': 'Brands',     'description': 'برندها'},
        {'name': 'Banners',    'description': 'بنرهای تبلیغاتی'},
        {'name': 'Products',   'description': 'محصولات'},
        {'name': 'Carts',      'description': 'سبد خرید'},
        {'name': 'Coupons',    'description': 'کدهای تخفیف'},
        {'name': 'Orders',     'description': 'سفارشات'},
    ],

    'POSTPROCESSING_HOOKS': [
        'config.spectacular.custom_postprocessing_hook',
    ],

    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# ======== Shop ========
# هزینه ارسال ثابت (تومان) - فقط سمت سرور تعیین می‌شود، نه توسط کاربر
SHOP_SHIPPING_COST = 50000

# ======== CORS ========
# ✅ برای development: همه originها مجاز
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ======== Celery ========
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60   # ۳۰ دقیقه