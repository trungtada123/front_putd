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
                        {"text": f"""Bạn là trợ lý đầu tư tài chính, giúp người dùng với các câu hỏi về đầu tư chứng khoán và quản lý danh mục. 
                         Hãy trả lời ngắn gọn, hữu ích và chuyên nghiệp.
                         Sử dụng markdown để định dạng câu trả lời:
                         - Sử dụng **văn bản** để in đậm các đầu mục quan trọng
                         - Sử dụng * hoặc - để tạo điểm đánh dấu danh sách
                         - Nếu có danh sách có số, hãy định dạng như: 1. **Tiêu đề:** nội dung
                         - Sử dụng xuống dòng để tách các ý
                         
                         Tin nhắn của người dùng: {message}"""}
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