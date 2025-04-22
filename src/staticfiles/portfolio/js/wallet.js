/**
 * Wallet and Banking Functionality for Portfolio Management System
 */
document.addEventListener('DOMContentLoaded', function() {
    // Xử lý hiển thị tên ngân hàng khác khi chọn "Ngân hàng khác"
    const bankSelect = document.getElementById('id_bank_name');
    const otherBankGroup = document.getElementById('otherBankGroup');
    
    if (bankSelect) {
        bankSelect.addEventListener('change', function() {
            if (this.value === 'other') {
                otherBankGroup.classList.remove('d-none');
            } else {
                otherBankGroup.classList.add('d-none');
            }
        });
    }
    
    // Xử lý phương thức thanh toán nạp tiền
    const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
    const bankTransferSection = document.getElementById('bankTransferSection');
    const momoSection = document.getElementById('momoSection');
    const vnpaySection = document.getElementById('vnpaySection');
    
    // Các trường VNPay
    const fullNameField = document.getElementById('fullName');
    const emailField = document.getElementById('email');
    
    // Hàm xử lý việc bật/tắt các trường dựa trên phương thức thanh toán
    function toggleRequiredFields() {
        // Nếu đang sử dụng VNPay, bật required cho các trường VNPay
        if (fullNameField && emailField) {
            if (vnpaySection && !vnpaySection.classList.contains('d-none')) {
                fullNameField.disabled = false;
                emailField.disabled = false;
            } else {
                fullNameField.disabled = true;
                emailField.disabled = true;
            }
        }
    }
    
    if (paymentMethods && paymentMethods.length > 0) {
        // Mặc định ẩn các trường khi trang tải
        toggleRequiredFields();
        
        paymentMethods.forEach(method => {
            method.addEventListener('change', function() {
                // Ẩn tất cả các phương thức
                if (bankTransferSection) bankTransferSection.classList.add('d-none');
                if (momoSection) momoSection.classList.add('d-none');
                if (vnpaySection) vnpaySection.classList.add('d-none');
                
                // Hiển thị phương thức được chọn
                if (this.value === 'bank_transfer' && bankTransferSection) {
                    bankTransferSection.classList.remove('d-none');
                } else if (this.value === 'momo' && momoSection) {
                    momoSection.classList.remove('d-none');
                } else if (this.value === 'vnpay' && vnpaySection) {
                    vnpaySection.classList.remove('d-none');
                }
                
                // Cập nhật các trường required
                toggleRequiredFields();
            });
        });
    }
    
    // Xử lý hiển thị số tiền nạp/rút và phí
    const amountInput = document.getElementById('amount');
    const amountDisplays = document.querySelectorAll('.amount-display');
    const feeDisplay = document.querySelector('.fee-display');
    const totalAmountDisplay = document.querySelector('.total-amount-display');
    
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            const amount = this.value ? parseInt(this.value) : 0;
            const formattedAmount = amount.toLocaleString('vi-VN') + ' VNĐ';
            
            // Cập nhật hiển thị số tiền
            if (amountDisplays) {
                amountDisplays.forEach(display => {
                    display.textContent = formattedAmount;
                });
            }
            
            // Xử lý tính phí rút tiền nếu đang ở trang rút tiền
            if (feeDisplay && totalAmountDisplay) {
                // Tính phí rút tiền (0.5%, tối thiểu 10,000, tối đa 50,000)
                let fee = Math.round(amount * 0.005);
                if (fee < 10000) fee = amount > 0 ? 10000 : 0;
                if (fee > 50000) fee = 50000;
                
                const formattedFee = fee.toLocaleString('vi-VN') + ' VNĐ';
                
                // Tính tổng số tiền nhận
                const totalAmount = amount - fee;
                const formattedTotalAmount = totalAmount > 0 ? totalAmount.toLocaleString('vi-VN') + ' VNĐ' : '0 VNĐ';
                
                // Cập nhật hiển thị
                feeDisplay.textContent = formattedFee;
                totalAmountDisplay.textContent = formattedTotalAmount;
            }
        });
        
        // Kích hoạt sự kiện input để cập nhật giá trị ban đầu
        const event = new Event('input', { bubbles: true });
        amountInput.dispatchEvent(event);
    }
}); 