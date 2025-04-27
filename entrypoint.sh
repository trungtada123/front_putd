#!/bin/sh

set -e

echo "Load environment variables"
export $(grep -v '^#' .env | grep -E '^[A-Za-z_][A-Za-z0-9_]*=.*$' | sed 's/[[:space:]]*$//' | xargs)
echo "Load environment variables completely."


# Wait for the database to be ready
echo "Waiting for database..."
until pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER; do
  echo "Database is not ready yet, waiting..."
  sleep 2
done
echo "Database is ready!"


# Chạy migration
echo "Start application..."
python src/manage.py makemigrations || { echo "❌ Lỗi tạo migrations"; exit 1; }
python src/manage.py migrate || { echo "❌ Lỗi migrate database"; exit 1; }


# Tạo admin user
echo "👤 Tạo tài khoản admin"
python src/manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if User.objects.filter(username='admin').exists():
    User.objects.filter(username='admin').delete()
    print('Đã xóa tài khoản admin cũ')
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print('✅ Đã tạo tài khoản admin mới')
"


# Ensure static directories exist
echo "📁 Creating static directories..."
mkdir -p /app/static/portfolio/css
mkdir -p /app/static/portfolio/img
mkdir -p /app/static/portfolio/js
chmod -R 755 /app/static

# Collect static files with verbose output
echo "📂 Collecting static files..."
python src/manage.py collectstatic --noinput -v 2 || { echo "❌ Lỗi collect static files"; exit 1; }

# Verify static files existence
echo "🔍 Verifying static files..."
if [ -d "/app/static" ]; then
  echo "✅ Static directory exists"
  ls -la /app/static
  if [ -d "/app/static/portfolio" ]; then
    echo "✅ Portfolio directory exists"
    ls -la /app/static/portfolio
  else
    echo "❌ Portfolio directory missing"
  fi
else
  echo "❌ Static directory missing"
fi


# Khởi động server bằng lệnh trong Dockerfile
echo "Start server..."
exec "$@"



# converting file entrypoint.sh to Unix format
# dos2unix entrypoint.sh
