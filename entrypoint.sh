#!/bin/bash
set -e  # Dung script neu co loi

echo "=== Kiểm tra kết nối PostgreSQL ==="
# Chờ DB sẵn sàng
echo "⏳ Chờ PostgreSQL khởi động..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ PostgreSQL đã sẵn sàng"

echo "=== Khởi tạo môi trường ==="

# Tạo các thư mục cần thiết
mkdir -p src/static src/media data/stock_data

# Kiểm tra xem đã có file .env chưa, nếu chưa thì tạo
if [ ! -f "/app/.env" ]; then
  echo "Tạo file .env với cấu hình mặc định..."
  cat > /app/.env << EOF
DEBUG=True
SECRET_KEY=django-insecure-default-key-for-development
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
DATABASE_URL=postgres://postgres:123456@db:5432/db_for_pm
EOF
fi

# Di chuyển vào thư mục src
cd /app/src

# Migrate database
echo "=== Thực hiện migrate ==="
python manage.py makemigrations
python manage.py migrate

# Xóa và tạo lại superuser
echo "=== Xóa và tạo lại tài khoản admin ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if User.objects.filter(username='admin').exists():
    User.objects.filter(username='admin').delete()
    print('Đã xóa tài khoản admin cũ')
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print('✅ Đã tạo tài khoản admin mới')
"

# Collect static files
echo "=== Thu thập static files ==="
python manage.py collectstatic --noinput

# Khởi động ứng dụng
echo "🚀 Khởi chạy Django server"
python manage.py runserver 0.0.0.0:8000
