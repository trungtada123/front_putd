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
    
    // Tìm hoặc tạo phần tử chứa mã QR
    let qrCodeContainer = document.getElementById('qrCodeContainer');
    if (!qrCodeContainer && bankTransferSection) {
        // Nếu không tìm thấy qrCodeContainer, tạo mới và thêm vào bankTransferSection
        qrCodeContainer = document.createElement('div');
        qrCodeContainer.id = 'qrCodeContainer';
        qrCodeContainer.className = 'mt-3 mb-3';
        
        // Thêm vào đầu hoặc cuối của bankTransferSection
        bankTransferSection.appendChild(qrCodeContainer);
        console.log('Đã tạo phần tử chứa mã QR');
    }
    
    // Hàm tạo mã QR cho chuyển khoản ngân hàng
    function generateQRCode(amount, transactionId, username) {
        // Thông tin ngân hàng mặc định (MB Bank)
        const BANK_ID = "MB";
        const ACCOUNT_NO = "0967720844";
        
        // Tạo nội dung chuyển khoản
        let transferContent = transactionId;
        if (amount) {
            transferContent += ` ${amount}`;
        }
        if (username) {
            transferContent += ` ${username}`;
        }
        
        // Tạo URL QR code từ VietQR
        const qrUrl = `https://img.vietqr.io/image/${BANK_ID}-${ACCOUNT_NO}-compact2.png?amount=${amount}&addInfo=${encodeURIComponent(transferContent)}`;
        
        console.log('URL mã QR:', qrUrl);
        return qrUrl;
    }
    
    // Hàm hiển thị mã QR
    function displayQRCode() {
        try {
            // Nếu không có container hoặc không tìm thấy bankTransferSection, tạo lại container
            if (!qrCodeContainer && bankTransferSection) {
                qrCodeContainer = document.createElement('div');
                qrCodeContainer.id = 'qrCodeContainer';
                qrCodeContainer.className = 'mt-3 mb-3';
                bankTransferSection.appendChild(qrCodeContainer);
                console.log('Tạo lại container mã QR');
            }
            
            if (!qrCodeContainer) {
                console.error('Không tìm thấy phần tử chứa mã QR');
                return;
            }
            
            // Lấy thông tin giao dịch
            const amount = document.getElementById('amount') ? document.getElementById('amount').value : 0;
            // Sử dụng một ID giao dịch tạm thời nếu không có sẵn
            const transactionId = document.getElementById('transaction_id') ? 
                document.getElementById('transaction_id').value : 
                'TX' + new Date().getTime().toString().slice(-6); // Mã ngắn hơn
            
            // Lấy tên người dùng từ phần tử có id là username hoặc lấy từ localStorage nếu có
            let username = '';
            if (document.getElementById('username')) {
                username = document.getElementById('username').value;
            } else if (localStorage.getItem('username')) {
                username = localStorage.getItem('username');
            }
            
            // Tạo URL mã QR
            const qrImageUrl = generateQRCode(amount, transactionId, username);
            
            // Tạo và hiển thị mã QR
            qrCodeContainer.innerHTML = `
                <div class="text-center mb-3 p-3 border rounded">
                    <h5 class="fw-bold">Quét mã QR để chuyển khoản nhanh</h5>
                    <div class="my-3">
                        <img src="${qrImageUrl}" alt="Mã QR chuyển khoản" class="img-fluid" style="max-width: 250px;">
                    </div>
                    <div class="mt-2 small">
                        <p class="mb-1"><strong>Ngân hàng:</strong> MB Bank</p>
                        <p class="mb-1"><strong>Số tài khoản:</strong> 0967720844</p>
                        <p class="mb-1"><strong>Số tiền:</strong> ${parseInt(amount).toLocaleString('vi-VN')} VNĐ</p>
                        <p class="mb-1"><strong>Nội dung CK:</strong> ${transactionId} ${amount} ${username}</p>
                    </div>
                </div>
            `;
            console.log('Đã hiển thị mã QR thành công');
        } catch (error) {
            console.error('Lỗi khi hiển thị mã QR:', error);
            if (qrCodeContainer) {
                qrCodeContainer.innerHTML = `
                    <div class="alert alert-danger">
                        Không thể hiển thị mã QR. Lỗi: ${error.message}
                    </div>
                `;
            }
        }
    }
    
    // Hiển thị mã QR khi trang vừa tải xong
    if (bankTransferSection && !bankTransferSection.classList.contains('d-none')) {
        setTimeout(displayQRCode, 500); // Đợi 500ms để đảm bảo trang đã tải xong
    }
    
    if (paymentMethods && paymentMethods.length > 0) {
        paymentMethods.forEach(method => {
            method.addEventListener('change', function() {
                // Ẩn tất cả các phương thức
                if (bankTransferSection) bankTransferSection.classList.add('d-none');
                
                // Hiển thị phương thức được chọn
                if (this.value === 'bank_transfer' && bankTransferSection) {
                    bankTransferSection.classList.remove('d-none');
                    // Hiển thị mã QR khi chọn phương thức chuyển khoản
                    setTimeout(displayQRCode, 300); // Đợi DOM cập nhật
                }
            });
        });
        
        // Nếu đã chọn phương thức chuyển khoản ngân hàng, hiển thị mã QR ngay
        const selectedMethod = document.querySelector('input[name="payment_method"]:checked');
        if (selectedMethod && selectedMethod.value === 'bank_transfer' && bankTransferSection) {
            if (!bankTransferSection.classList.contains('d-none')) {
                setTimeout(displayQRCode, 500);
            }
        }
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
            
            // Cập nhật mã QR khi số tiền thay đổi
            if (bankTransferSection && !bankTransferSection.classList.contains('d-none')) {
                displayQRCode();
            }
        });
        
        // Kích hoạt sự kiện input để cập nhật giá trị ban đầu
        const event = new Event('input', { bubbles: true });
        amountInput.dispatchEvent(event);
    } else {
        console.warn('Không tìm thấy phần tử nhập số tiền');
    }
}); 