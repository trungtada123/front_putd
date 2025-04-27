FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc netcat-openbsd postgresql-client dos2unix && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

COPY . /app
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "=== Kiểm tra kết nối PostgreSQL ===" ' >> /app/entrypoint.sh && \
    echo '# Chờ DB sẵn sàng' >> /app/entrypoint.sh && \
    echo 'echo "⏳ Chờ PostgreSQL khởi động..."' >> /app/entrypoint.sh && \
    echo 'while ! nc -z db 5432; do' >> /app/entrypoint.sh && \
    echo '  sleep 1' >> /app/entrypoint.sh && \
    echo 'done' >> /app/entrypoint.sh && \
    echo 'echo "✅ PostgreSQL đã sẵn sàng"' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "=== Khởi tạo môi trường ==="' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Tạo các thư mục cần thiết' >> /app/entrypoint.sh && \
    echo 'mkdir -p src/static src/media data/stock_data' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Di chuyển vào thư mục src' >> /app/entrypoint.sh && \
    echo 'cd /app/src' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Migrate database' >> /app/entrypoint.sh && \
    echo 'echo "=== Thực hiện migrate ==="' >> /app/entrypoint.sh && \
    echo 'python manage.py makemigrations' >> /app/entrypoint.sh && \
    echo 'python manage.py migrate' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Xóa và tạo lại superuser' >> /app/entrypoint.sh && \
    echo 'echo "=== Xóa và tạo lại tài khoản admin ==="' >> /app/entrypoint.sh && \
    echo 'python manage.py shell -c "' >> /app/entrypoint.sh && \
    echo 'from django.contrib.auth import get_user_model;' >> /app/entrypoint.sh && \
    echo 'User = get_user_model();' >> /app/entrypoint.sh && \
    echo 'if User.objects.filter(username=\"admin\").exists():' >> /app/entrypoint.sh && \
    echo '    User.objects.filter(username=\"admin\").delete()' >> /app/entrypoint.sh && \
    echo '    print(\"Đã xóa tài khoản admin cũ\")' >> /app/entrypoint.sh && \
    echo 'User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin123\")' >> /app/entrypoint.sh && \
    echo 'print(\"✅ Đã tạo tài khoản admin mới\")' >> /app/entrypoint.sh && \
    echo '"' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Collect static files' >> /app/entrypoint.sh && \
    echo 'echo "=== Thu thập static files ==="' >> /app/entrypoint.sh && \
    echo 'python manage.py collectstatic --noinput' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Khởi động ứng dụng' >> /app/entrypoint.sh && \
    echo 'echo "🚀 Khởi chạy Django server"' >> /app/entrypoint.sh && \
    echo 'python manage.py runserver 0.0.0.0:8000' >> /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
