# Hệ thống Quản lý Danh mục Đầu tư

Hệ thống quản lý danh mục đầu tư chứng khoán với các tính năng quản lý, phân tích và theo dõi danh mục cổ phiếu.

## Yêu cầu hệ thống

- Python 3.9+ 
- PostgreSQL 12+
- Các thư viện Python (xem file requirements.txt)

## Lưu ý quan trọng khi clone repository

Khi clone repository này, cần lưu ý một số vấn đề sau:

1. **Cài đặt thư viện VNStock**: Dự án sử dụng thư viện `vnstock` để lấy thông tin cổ phiếu. Cần cài đặt thư viện này đúng phiên bản:
   ```
   pip install vnstock==3.1.0.2
   ```

2. **Tệp AstroBot**: Chatbot AstroBot sử dụng các tệp JavaScript và CSS đặc biệt. Đảm bảo các tệp sau được tải về đầy đủ:
   - `src/static/portfolio/js/chat.js`
   - `src/static/portfolio/css/chat-animations.css` 
   - `src/static/portfolio/css/styles.css`
   - `src/static/portfolio/img/astrobot.jpg`

3. **Cấu hình PostgreSQL**: Đảm bảo PostgreSQL đã được cài đặt và cấu hình đúng theo thông số trong file `run.bat` hoặc `entrypoint.sh`.

## Cài đặt

1. Clone repository:
   ```
   git clone <url-repository>
   ```

2. Cài đặt các thư viện Python:
   ```
   pip install -r requirements.txt
   ```

3. Chạy script khởi tạo:
   - Windows: Chạy file `run.bat`
   - Linux/MacOS: Chạy file `entrypoint.sh`

4. Truy cập ứng dụng:
   - URL: http://localhost:8000

## Các tính năng chính

- Quản lý danh mục đầu tư
- Thống kê và phân tích hiệu suất
- Mua/bán cổ phiếu với dữ liệu thời gian thực
- AstroBot hỗ trợ tư vấn đầu tư

# Hệ Thống Quản Lý Danh Mục Đầu Tư

- **Thành viên nhóm**
- **Thành viên 1**: Nguyễn Thị Thúy Kiều - 22733091
- **Thành viên 2**: Đào Tiến Sang - 22705971
- **Thành viên 3**: Nguyễn Chí Trung - 22719231
- **Thành viên 4**: Kiều Trương Hàm Hương - 22642961


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
$ git clone https://github.com/trungtada123/PortfolioManagement_DTDM.git
```
### 2. Cài đặt App
```bash
$ ./run.bat
```

### 3. Run docker:
```bash
$ docker-compose up --build
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
Hệ thống sẽ chạy tại `http://127.0.0.1:8000/`.


## Thiết lập dữ liệu cổ phiếu sau khi clone repository

Sau khi clone repository và cấu hình cơ sở dữ liệu, bạn cần thêm dữ liệu cổ phiếu để chức năng mua/bán hoạt động:

### Cách 1: Đồng bộ dữ liệu từ VNStock (khuyên dùng)

```bash
python manage.py shell
```

```python
from portfolio.vnstock_services import sync_vnstock_to_assets_fixed

def sync_vnstock_to_assets_fixed():
    """Đồng bộ dữ liệu từ vnstock vào model Asset - fixed version"""
    from portfolio.models import Asset
    from vnstock import Vnstock
    import pandas as pd
    from datetime import datetime
    
    try:
        # Khởi tạo vnstock instance
        vnstock_instance = Vnstock()
        stock = vnstock_instance.stock(symbol='VN30', source='VCI')
        
        # Lấy danh sách cổ phiếu
        symbols_df = stock.listing.all_symbols()
        print(f"Đã tìm thấy {len(symbols_df)} cổ phiếu")
        
        # Lấy tất cả mã cổ phiếu
        symbols = symbols_df['symbol'].tolist()
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Thêm cổ phiếu vào database
        for symbol in symbols:
            try:
                # Lấy thông tin từ dataframe
                symbol_info = symbols_df[symbols_df['symbol'] == symbol]
                
                if not symbol_info.empty:
                    name = symbol_info['organ_name'].iloc[0]
                    
                    # Cập nhật hoặc tạo mới
                    asset, created = Asset.objects.update_or_create(
                        symbol=symbol,
                        defaults={
                            'name': name or f"Cổ phiếu {symbol}",  # Đảm bảo name không bị null
                            'type': 'stock',
                            'sector': 'Unknown',
                            'current_price': 10000,  # Giá mặc định
                            'description': f"Imported from VNStock"
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    # In tiến độ
                    if (created_count + updated_count) % 100 == 0:
                        print(f"Đã xử lý {created_count + updated_count}/{len(symbols)} cổ phiếu")
            
            except Exception as e:
                error_count += 1
                print(f"Lỗi khi xử lý mã {symbol}: {str(e)}")
        
        # Kết quả
        result = {
            'created': created_count,
            'updated': updated_count,
            'errors': error_count,
            'total': created_count + updated_count
        }
        print(f"Kết quả: {result}")
        return result
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return {'created': 0, 'updated': 0, 'errors': 1, 'total': 0}

# Chạy function
result = sync_vnstock_to_assets_fixed()
print(result)
exit()
