/**
 * Wallet and Banking Functionality for Portfolio Management System
 */
document.addEventListener('DOMContentLoaded', function() {
    // Xử lý tài khoản ngân hàng khác trong form thêm tài khoản
    const bankNameSelect = document.getElementById('id_bank_name');
    const otherBankGroup = document.getElementById('otherBankGroup');
    
    if (bankNameSelect && otherBankGroup) {
        bankNameSelect.addEventListener('change', function() {
            if (this.value === 'other') {
                otherBankGroup.classList.remove('d-none');
            } else {
                otherBankGroup.classList.add('d-none');
            }
        });
    }
    
    // Xử lý hiển thị số tiền trong form nạp/rút tiền
    const amountInput = document.getElementById('amount');
    const amountDisplayElements = document.querySelectorAll('.amount-display');
    const feeDisplayElement = document.querySelector('.fee-display');
    const totalAmountDisplayElement = document.querySelector('.total-amount-display');
    
    if (amountInput && amountDisplayElements.length > 0) {
        amountInput.addEventListener('input', function() {
            const amount = parseFloat(this.value) || 0;
            const formattedAmount = amount.toLocaleString('vi-VN') + ' VNĐ';
            
            amountDisplayElements.forEach(element => {
                element.textContent = formattedAmount;
            });
            
            // Tính phí và tổng tiền cho form rút tiền
            if (feeDisplayElement && totalAmountDisplayElement) {
                const fee = Math.min(Math.max(amount * 0.005, 10000), 50000);
                const totalAmount = amount - fee;
                
                feeDisplayElement.textContent = fee.toLocaleString('vi-VN') + ' VNĐ';
                totalAmountDisplayElement.textContent = totalAmount.toLocaleString('vi-VN') + ' VNĐ';
            }
        });
    }
    
    // Xử lý hiển thị phương thức thanh toán trong form nạp tiền
    const paymentMethodRadios = document.querySelectorAll('input[name="payment_method"]');
    const bankTransferSection = document.getElementById('bankTransferSection');
    const momoSection = document.getElementById('momoSection');
    const vnpaySection = document.getElementById('vnpaySection');
    
    if (paymentMethodRadios.length > 0 && bankTransferSection && momoSection && vnpaySection) {
        paymentMethodRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                bankTransferSection.classList.add('d-none');
                momoSection.classList.add('d-none');
                vnpaySection.classList.add('d-none');
                
                if (this.value === 'bank_transfer') {
                    bankTransferSection.classList.remove('d-none');
                } else if (this.value === 'momo') {
                    momoSection.classList.remove('d-none');
                } else if (this.value === 'vnpay') {
                    vnpaySection.classList.remove('d-none');
                }
            });
        });
    }
}); 