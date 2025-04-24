import requests
import json
from django.conf import settings

def get_ai_response(message):
    """
    Gọi API Gemini để nhận phản hồi từ AI
    
    Args:
        message (str): Tin nhắn của người dùng
        
    Returns:
        str: Phản hồi từ AI hoặc thông báo lỗi
    """
    try:
        API_KEY = "AIzaSyB6UifFBfKbGgJmTGdPtyQW-OzaNRithOM"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"""Bạn là trợ lý đầu tư tài chính AstroBot, giúp người dùng với các câu hỏi về đầu tư chứng khoán và quản lý danh mục. 
                         Hãy trả lời ngắn gọn, hữu ích và chuyên nghiệp.
                         
                         Sử dụng các định dạng đặc biệt cho câu trả lời đẹp và ấn tượng:
                         
                         1. Tiêu đề và phần quan trọng:
                            - Sử dụng # để tạo tiêu đề chính
                            - Sử dụng ## và ### cho các tiêu đề phụ
                            - Sử dụng **đậm** cho các thuật ngữ quan trọng
                            - Sử dụng *nghiêng* cho các định nghĩa hoặc giải thích
                            - Sử dụng ==từ khóa== để highlight các khái niệm quan trọng
                            - Dùng ký hiệu như [123.456] cho các số liệu tài chính
                         
                         2. Danh sách và cấu trúc:
                            - Sử dụng dấu * hoặc - để tạo danh sách không thứ tự
                            - Sử dụng 1., 2., v.v. để tạo danh sách có thứ tự
                            - Sử dụng > để tạo blockquote cho các thông tin quan trọng
                            
                         3. Cards và thông tin đặc biệt:
                            - Sử dụng [info]...[/info] để tạo khung thông tin
                            - Sử dụng [warning]...[/warning] cho cảnh báo
                            - Sử dụng [success]...[/success] cho các mẹo hữu ích
                         
                         4. Bảng:
                            - Sử dụng định dạng bảng markdown cho dữ liệu có cấu trúc. Ví dụ:
                            
                            | Cột 1 | Cột 2 | Cột 3 |
                            |-------|-------|-------|
                            | Dữ liệu 1 | Dữ liệu 2 | Dữ liệu 3 |
                         
                         Trả lời phải đẹp, có cấu trúc rõ ràng, sử dụng 1-2 emoji phù hợp nếu cần thiết.

                         Người dùng yêu cầu: {message}"""}
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Đã xảy ra lỗi khi kết nối với API: {response.status_code}"
    
    except Exception as e:
        return f"Đã xảy ra lỗi: {str(e)}" 

def generate_qr_code(amount, transaction_id, username=None):
    """
    Tạo QR code VietQR cho giao dịch chuyển khoản ngân hàng
    
    Args:
        amount (float): Số tiền cần chuyển khoản
        transaction_id (str): Mã giao dịch để ghi trong nội dung chuyển khoản
        username (str, optional): Tên người dùng để thêm vào nội dung chuyển khoản
        
    Returns:
        str: URL của hình ảnh QR code
    """
    # Thông tin ngân hàng mặc định (MB Bank)
    BANK_ID = "MB"
    ACCOUNT_NO = "0967720844"
    
    # Tạo nội dung chuyển khoản bao gồm mã giao dịch, số tiền và tên người dùng
    transfer_content = transaction_id
    if amount:
        transfer_content += f" {amount}"
    if username:
        transfer_content += f" {username}"
    
    # Tạo URL QR code từ VietQR
    qr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?amount={amount}&addInfo={transfer_content}"
    
    return qr_url 