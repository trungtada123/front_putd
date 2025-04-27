# Hướng dẫn chạy dự án với Docker

## Yêu cầu

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Các bước cài đặt

### 1. Clone dự án

```bash
git clone <url_repository>
cd front_putd
```

### 2. Tạo file .env

Tạo file `.env` trong thư mục gốc của dự án với nội dung sau:

```
DEBUG=True
SECRET_KEY=django-insecure-default-key-for-development
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
DATABASE_URL=postgres://postgres:123456@db:5432/db_for_pm
```

### 3. Khởi động Docker Compose

```bash
docker-compose up --build
```

Điều này sẽ:
- Build Docker image
- Khởi động container PostgreSQL
- Khởi động container ứng dụng Django
- Thực hiện migrate database
- Khởi tạo tài khoản admin

### 4. Truy cập ứng dụng

Sau khi các container được khởi động thành công:

- Web app: http://localhost:8000
- Admin site: http://localhost:8000/admin
  - Username: admin
  - Password: admin123

## Các lệnh hữu ích

### Chạy trong background

```bash
docker-compose up -d
```

### Dừng các container

```bash
docker-compose down
```

### Xem logs

```bash
docker-compose logs -f
```

### Xem logs của container cụ thể

```bash
docker-compose logs -f web
```

### Thực hiện lệnh Django

```bash
docker-compose exec web python src/manage.py <command>
```

Ví dụ:
```bash
docker-compose exec web python src/manage.py makemigrations
docker-compose exec web python src/manage.py migrate
docker-compose exec web python src/manage.py createsuperuser
```

### Xóa hoàn toàn các volumes

```bash
docker-compose down -v
```

## Cấu trúc dự án

```
front_putd/
├── data/                  # Dữ liệu
├── src/                   # Source code Django
│   ├── config/            # Cấu hình Django
│   ├── portfolio/         # App chính
│   ├── static/            # Static files
│   ├── media/             # Media files
│   ├── templates/         # Templates
│   └── manage.py          # Django management script
├── Dockerfile             # Cấu hình build Docker image
├── docker-compose.yml     # Cấu hình Docker Compose
├── entrypoint.sh          # Script khởi động container
├── requirements.txt       # Dependencies Python
└── .env                   # Biến môi trường
``` 