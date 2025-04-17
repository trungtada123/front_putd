from datetime import datetime
from vnstock import Vnstock

# Khởi tạo đối tượng Vnstock với mã cổ phiếu mặc định
vnstock_instance = Vnstock()
stock = vnstock_instance.stock(symbol='VN30', source='VCI')

def get_list_stock_market():
    return stock.listing.all_symbols()['ticker'].values      # danh sách các mã chứng khoán niêm yết

# - hàm lấy mã cổ phiếu và tên công ty
def get_ticker_companyname():
    list_ticker = [
        {"ticker": row[0], "organ_name": row[1]}
        for row in stock.listing.all_symbols().itertuples(index=False, name=None)
    ]
    return list_ticker

# - Lấy giá khớp lệnh gần nhất của cổ phiếu
def get_refer_price(stock_code):
    try:
        data = stock.trading.price_board(symbols_list=[stock_code])
        ref_price = int(data[('listing', 'ref_price')].iloc[0])
        return ref_price
    except Exception as e:
        return f'Không tìm thấy mã cổ phiếu {stock_code}!'

# ===== Lấy thông tin bảng giá thị trường ====
def get_price_board():
    symbols = stock.listing.all_symbols()['ticker'].values
    return stock.trading.price_board(symbols_list=list(symbols))

# ==== Lấy giá lịch sử ====
def get_historical_data(symbol):
    try:
        # Lấy dữ liệu lịch sử từ ngày 2000-01-01 đến hiện tại
        today = datetime.now().strftime('%Y-%m-%d')
        data = stock.quote.history(symbol=symbol, start='2000-01-01', end=today)
        
        # Đảm bảo cột time tồn tại và có định dạng đúng
        if 'time' not in data.columns and data.index.name != 'time':
            data = data.reset_index()  # Chuyển index thành cột nếu index là ngày
            if 'index' in data.columns:
                data = data.rename(columns={'index': 'time'})
                
        print(f"Data columns: {data.columns}")  # Debug log
        print(f"Sample data:\n{data.head()}")   # Debug log
        
        return data
    except Exception as e:
        print(f"Error in get_historical_data: {str(e)}")  # Debug log
        raise Exception(f"Không thể lấy dữ liệu lịch sử cho mã {symbol}: {str(e)}") 