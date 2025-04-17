#!/bin/sh

set -e  # Dừng script nếu có lỗi

echo "=== Kiểm tra PostgreSQL CLI ==="
if ! command -v psql >/dev/null 2>&1; then
    echo "❌ PostgreSQL chưa được cài hoặc không có trong PATH"
    exit 1
fi

echo "=== Khởi tạo môi trường ==="

# Xoá database SQLite cũ nếu có
if [ -f "src/db.sqlite3" ]; then
    rm src/db.sqlite3
fi

# Cài requirements
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Tạo thư mục static, media, data
mkdir -p src/static src/media data/stock_data

# Tạo file settings.py
echo "Đang tạo config/settings.py..."

cat <<EOF > src/config/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-default-key-for-development'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'portfolio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_for_pm',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'db',  # sử dụng service name trong docker-compose
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

AUTH_USER_MODEL = 'portfolio.User'
EOF

# Chờ DB sẵn sàng
echo "⏳ Chờ PostgreSQL khởi động..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ PostgreSQL đã sẵn sàng"

# Reset database
echo "🧨 Xoá & tạo lại database PostgreSQL"
PGPASSWORD=123456 psql -h db -U postgres -c "DROP DATABASE IF EXISTS db_for_pm;"
PGPASSWORD=123456 psql -h db -U postgres -c "CREATE DATABASE db_for_pm WITH ENCODING='UTF8' TEMPLATE=template0;"

# Xoá & tạo lại migrations
rm -rf src/portfolio/migrations
mkdir -p src/portfolio/migrations
touch src/portfolio/migrations/__init__.py

# Migrate
cd src
python manage.py makemigrations portfolio || { echo "❌ Lỗi tạo migrations"; exit 1; }
python manage.py migrate || { echo "❌ Lỗi migrate database"; exit 1; }

# Tạo admin user nếu chưa có
echo "👤 Tạo tài khoản admin nếu chưa tồn tại"
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
else:
    print('Admin đã tồn tại')
"

# Chạy server
echo "🚀 Khởi chạy Django server tại 0.0.0.0:8000"
python manage.py runserver 0.0.0.0:8000
