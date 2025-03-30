@echo off
SETLOCAL EnableDelayedExpansion

echo === Kiem tra PostgreSQL ===
psql --version > nul 2>&1
if errorlevel 1 (
    echo Loi: PostgreSQL chua duoc cai dat hoac chua duoc them vao PATH
    echo Vui long cai dat PostgreSQL va dam bao no duoc them vao PATH
    pause
    exit /b 1
)

echo === Khoi tao moi truong ===

REM Xoa moi truong ao cu neu ton tai
if exist venv (
    rmdir /s /q venv
    timeout /t 2 /nobreak >nul
)

REM Tao va kich hoat moi truong ao moi
python -m venv venv
call venv\Scripts\activate.bat

REM Cap nhat pip va cai dat cac goi co ban
python -m pip install --upgrade pip
python -m pip install wheel setuptools

REM Di chuyen vao thu muc src
cd src

REM Xoa database cu neu co
if exist db.sqlite3 (
    del db.sqlite3
)

REM Cai dat cac goi tu requirements.txt
python -m pip install -r requirements.txt

REM Tao cac thu muc can thiet
if not exist static mkdir static
if not exist media mkdir media
if not exist ..\data\stock_data mkdir ..\data\stock_data

REM Tao file settings.py moi voi cau hinh PostgreSQL
echo Dang tao file settings.py...
(
echo import os
echo from pathlib import Path
echo.
echo BASE_DIR = Path^(__file__^).resolve^(^).parent.parent
echo.
echo SECRET_KEY = 'django-insecure-default-key-for-development'
echo.
echo DEBUG = True
echo.
echo ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
echo.
echo INSTALLED_APPS = [
echo     'django.contrib.admin',
echo     'django.contrib.auth',
echo     'django.contrib.contenttypes',
echo     'django.contrib.sessions',
echo     'django.contrib.messages',
echo     'django.contrib.staticfiles',
echo     'crispy_forms',
echo     'crispy_bootstrap5',
echo     'portfolio',
echo ]
echo.
echo MIDDLEWARE = [
echo     'django.middleware.security.SecurityMiddleware',
echo     'django.contrib.sessions.middleware.SessionMiddleware',
echo     'django.middleware.common.CommonMiddleware',
echo     'django.middleware.csrf.CsrfViewMiddleware',
echo     'django.contrib.auth.middleware.AuthenticationMiddleware',
echo     'django.contrib.messages.middleware.MessageMiddleware',
echo     'django.middleware.clickjacking.XFrameOptionsMiddleware',
echo ]
echo.
echo ROOT_URLCONF = 'config.urls'
echo.
echo TEMPLATES = [
echo     {
echo         'BACKEND': 'django.template.backends.django.DjangoTemplates',
echo         'DIRS': [BASE_DIR / 'templates'],
echo         'APP_DIRS': True,
echo         'OPTIONS': {
echo             'context_processors': [
echo                 'django.template.context_processors.debug',
echo                 'django.template.context_processors.request',
echo                 'django.contrib.auth.context_processors.auth',
echo                 'django.contrib.messages.context_processors.messages',
echo             ],
echo         },
echo     },
echo ]
echo.
echo WSGI_APPLICATION = 'config.wsgi.application'
echo.
echo DATABASES = {
echo     'default': {
echo         'ENGINE': 'django.db.backends.postgresql',
echo         'NAME': 'db_for_pm',
echo         'USER': 'postgres',
echo         'PASSWORD': '123456',
echo         'HOST': 'localhost',
echo         'PORT': '5432',
echo     }
echo }
echo.
echo AUTH_PASSWORD_VALIDATORS = [
echo     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
echo     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
echo     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
echo     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
echo ]
echo.
echo LANGUAGE_CODE = 'vi'
echo TIME_ZONE = 'Asia/Ho_Chi_Minh'
echo USE_I18N = True
echo USE_TZ = True
echo.
echo STATIC_URL = 'static/'
echo STATICFILES_DIRS = [BASE_DIR / 'static']
echo STATIC_ROOT = BASE_DIR / 'staticfiles'
echo.
echo MEDIA_URL = 'media/'
echo MEDIA_ROOT = BASE_DIR / 'media'
echo.
echo DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
echo.
echo CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
echo CRISPY_TEMPLATE_PACK = "bootstrap5"
echo.
echo LOGIN_URL = 'login'
echo LOGIN_REDIRECT_URL = 'dashboard'
echo LOGOUT_REDIRECT_URL = 'home'
echo.
echo AUTH_USER_MODEL = 'portfolio.User'
) > config\settings.py

REM Tao database PostgreSQL
echo === Tao database PostgreSQL ===
set PGPASSWORD=123456
psql -U postgres -c "DROP DATABASE IF EXISTS db_for_pm;"
psql -U postgres -c "CREATE DATABASE db_for_pm WITH ENCODING='UTF8' TEMPLATE=template0;"

REM Xoa migrations cu
rmdir /s /q portfolio\migrations
mkdir portfolio\migrations
type nul > portfolio\migrations\__init__.py

REM Tao migrations moi va ap dung
python manage.py makemigrations portfolio
if errorlevel 1 (
    echo Loi: Khong the tao migrations
    pause
    exit /b 1
)

python manage.py migrate
if errorlevel 1 (
    echo Loi: Khong the ap dung migrations
    echo Kiem tra lai ket noi PostgreSQL
    pause
    exit /b 1
)

REM Tao superuser
echo.
echo === Tao tai khoan admin ===
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin da ton tai')"

REM Mo trinh duyet
start http://127.0.0.1:8000

REM Chay server
echo === Khoi dong server ===
python manage.py runserver

ENDLOCAL 