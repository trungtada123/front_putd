# Hệ Thống Quản Lý Danh Mục Đầu Tư

## Giới Thiệu
Hệ thống quản lý danh mục đầu tư giúp người dùng theo dõi, mua bán tài sản tài chính và quản lý danh mục đầu tư của họ. Hệ thống cung cấp các chức năng như nạp tiền vào ví, giao dịch tài sản, theo dõi biến động thị trường, và báo cáo hiệu suất danh mục.

## Công Nghệ Sử Dụng
- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **Authentication**: Django Authentication

## Các Tính Năng Chính
- Đăng ký, đăng nhập, xác thực người dùng
- Quản lý ví tiền, nạp tiền vào ví
- Tạo và quản lý danh mục đầu tư
- Mua, bán tài sản tài chính
- Theo dõi biến động giá thị trường
- Xem báo cáo hiệu suất danh mục đầu tư

## Cấu Trúc Cơ Sở Dữ Liệu
Hệ thống bao gồm các bảng chính:

1. **Users**: Quản lý thông tin người dùng
2. **Wallets**: Quản lý số dư của người dùng
3. **Deposits**: Lưu lịch sử nạp tiền
4. **Portfolios**: Quản lý danh mục đầu tư
5. **Assets**: Lưu danh sách tài sản tài chính
6. **Portfolio_Assets**: Lưu tài sản trong danh mục đầu tư
7. **Transactions**: Lưu lịch sử mua bán tài sản
8. **Market_Data**: Cập nhật giá tài sản theo thời gian
9. **Performance_Reports**: Báo cáo hiệu suất danh mục

## Hướng Dẫn Cài Đặt
### 1. Clone repository
```bash
$ git clone https://github.com/iuh-application-development/portfolio_management.git
$ cd 
```
### 2. Cài đặt môi trường ảo
```bash
$ python -m venv venv
$ source venv/bin/activate  # Trên Linux/macOS
$ venv\Scripts\activate    # Trên Windows
```
### 3. Cài đặt dependencies
```bash
$ pip install -r requirements.txt
```
### 4. Cấu hình PostgreSQL
Cập nhật file `.env` với thông tin database:
```
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```
### 5. Chạy migration
```bash
$ python manage.py migrate
```
### 6. Chạy server
```bash
$ python manage.py runserver
```
Hệ thống sẽ chạy tại `http://127.0.0.1:8000/`.

