import re
import json
import requests
from decimal import Decimal
from django.conf import settings

def check_paid(transaction_id, amount):
    """
    Xác minh giao dịch chuyển khoản từ API
    
    Args:
        transaction_id (str): Mã giao dịch cần kiểm tra
        amount (Decimal): Số tiền của giao dịch
        
    Returns:
        dict: Kết quả kiểm tra với các thông tin:
            - success (bool): True nếu xác minh thành công, False nếu thất bại
            - message (str): Thông báo kết quả
            - transaction_detail (dict, optional): Chi tiết giao dịch nếu tìm thấy
    """
    try:
        # Giả lập API trả về kết quả
        # Trong thực tế, đây sẽ là một API call đến ngân hàng hoặc hệ thống thanh toán
        # Ví dụ: response = requests.get(f"{settings.PAYMENT_API_URL}/transaction/{transaction_id}")
        
        # Giả lập kết quả API - Trong thực tế, dữ liệu này sẽ từ API thật
        mock_api_data = {
            "DEP20A59ACB": {
                "Thời gian": "2023-09-30 15:45:22",
                "Mô tả": "DEP20A59ACB CHUYEN TIEN",
                "Giá trị": "1000000",
                "Mã giao dịch": "MB-123456789",
                "Trạng thái": "Thành công"
            },
            "DEP30B68DCF": {
                "Thời gian": "2023-10-01 10:15:45",
                "Mô tả": "DEP30B68DCF CHUYEN KHOAN",
                "Giá trị": "500000", 
                "Mã giao dịch": "MB-987654321",
                "Trạng thái": "Thành công"
            }
        }
        
        # Kiểm tra xem mã giao dịch có trong dữ liệu API không
        transaction_detail = mock_api_data.get(transaction_id)
        
        if not transaction_detail:
            return {
                "success": False,
                "message": f"Không tìm thấy giao dịch với mã {transaction_id}. Vui lòng kiểm tra lại mã giao dịch hoặc liên hệ admin nếu bạn đã chuyển khoản.",
            }
        
        # Trích xuất mã giao dịch từ mô tả giao dịch
        description = transaction_detail.get("Mô tả", "")
        transaction_code_match = re.search(r'^(\w+)', description)
        
        if not transaction_code_match:
            return {
                "success": False,
                "message": "Không thể xác minh mã giao dịch từ nội dung chuyển khoản. Vui lòng liên hệ admin.",
                "transaction_detail": transaction_detail
            }
        
        transaction_code = transaction_code_match.group(1)
        
        # Lấy số tiền từ API
        api_amount = Decimal(transaction_detail.get("Giá trị", "0"))
        
        # So sánh mã giao dịch và số tiền
        if transaction_code == transaction_id:
            if api_amount == amount:
                return {
                    "success": True,
                    "message": "Xác nhận nạp tiền thành công! Số dư tài khoản của bạn đã được cập nhật.",
                    "transaction_detail": transaction_detail
                }
            else:
                return {
                    "success": False,
                    "message": f"Mã giao dịch hợp lệ nhưng số tiền không khớp. Bạn đã chuyển {api_amount:,} VNĐ nhưng yêu cầu nạp {amount:,} VNĐ. Vui lòng liên hệ admin để được hỗ trợ.",
                    "transaction_detail": transaction_detail
                }
        else:
            return {
                "success": False,
                "message": f"Mã giao dịch trong nội dung chuyển khoản ({transaction_code}) không khớp với mã yêu cầu ({transaction_id}). Vui lòng liên hệ admin.",
                "transaction_detail": transaction_detail
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Lỗi khi xác minh giao dịch: {str(e)}. Vui lòng thử lại sau hoặc liên hệ admin."
        } 