from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import timedelta
import uuid

from .models import Wallet, BankAccount, WalletTransaction
from .forms import BankAccountForm, DepositForm, WithdrawForm

@login_required
def wallet(request):
    # Lấy hoặc tạo ví cho người dùng
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Lấy danh sách tài khoản ngân hàng
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    # Lấy giao dịch gần đây
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Lọc giao dịch theo loại nếu có tham số trong query
    transaction_type = request.GET.get('type')
    if transaction_type in ['deposit', 'withdraw']:
        transactions = transactions.filter(type=transaction_type)
    
    # Phân trang giao dịch
    paginator = Paginator(transactions, 10)  # 10 giao dịch mỗi trang
    page_number = request.GET.get('page')
    paged_transactions = paginator.get_page(page_number)
    
    # Tính tổng nạp/rút
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    total_deposit = WalletTransaction.objects.filter(
        user=request.user, 
        type='deposit', 
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_withdraw = WalletTransaction.objects.filter(
        user=request.user, 
        type='withdraw', 
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_deposit = WalletTransaction.objects.filter(
        user=request.user, 
        type='deposit', 
        status='completed',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_withdraw = WalletTransaction.objects.filter(
        user=request.user, 
        type='withdraw', 
        status='completed',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'wallet': wallet,
        'bank_accounts': bank_accounts,
        'transactions': paged_transactions,
        'total_deposit': total_deposit,
        'total_withdraw': total_withdraw,
        'monthly_deposit': monthly_deposit,
        'monthly_withdraw': monthly_withdraw
    }
    
    return render(request, 'portfolio/wallet.html', context)

@login_required
def deposit_money(request):
    # Lấy hoặc tạo ví cho người dùng
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Lấy danh sách tài khoản ngân hàng
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        form = DepositForm(request.user, request.POST)
        if form.is_valid():
            # Xử lý form nạp tiền
            amount = form.cleaned_data['amount']
            payment_method = form.cleaned_data['payment_method']
            bank_account = form.cleaned_data['bank_account']
            agree_terms = form.cleaned_data['agree_terms']
            
            # Xử lý tài khoản ngân hàng mới nếu có
            if bank_account == 'new':
                bank_name = form.cleaned_data['new_bank_name']
                other_bank_name = form.cleaned_data['new_other_bank_name']
                account_name = form.cleaned_data['new_account_name']
                account_number = form.cleaned_data['new_account_number']
                branch = form.cleaned_data['new_branch']
                is_default = form.cleaned_data['new_is_default']
                
                if bank_name == 'other' and other_bank_name:
                    display_name = other_bank_name
                else:
                    display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                
                # Tạo tài khoản ngân hàng mới
                bank_account = BankAccount.objects.create(
                    user=request.user,
                    bank_name=bank_name,
                    other_bank_name=other_bank_name,
                    account_name=account_name,
                    account_number=account_number,
                    branch=branch,
                    is_default=is_default
                )
                
                messages.success(request, f'Đã thêm tài khoản {display_name} - {account_number}')
            
            # Tạo giao dịch nạp tiền
            transaction = WalletTransaction.objects.create(
                user=request.user,
                wallet=wallet,
                type='deposit',
                amount=amount,
                fee=0,  # Miễn phí nạp tiền
                net_amount=amount,
                status='pending',
                bank_account=bank_account if bank_account != 'new' else bank_account,
                payment_method=payment_method,
                transaction_id=f"DEP{uuid.uuid4().hex[:8].upper()}",
                notes=f"Nạp tiền qua {dict(WalletTransaction.PAYMENT_METHOD_CHOICES)[payment_method]}"
            )
            
            messages.success(request, 'Yêu cầu nạp tiền đã được ghi nhận. Chúng tôi sẽ xử lý trong thời gian sớm nhất.')
            return redirect('wallet')
    else:
        form = DepositForm(request.user)
    
    context = {
        'wallet': wallet,
        'bank_accounts': bank_accounts,
        'form': form
    }
    
    return render(request, 'portfolio/deposit.html', context)

@login_required
def withdraw_money(request):
    # Lấy hoặc tạo ví cho người dùng
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Lấy danh sách tài khoản ngân hàng
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        form = WithdrawForm(request.user, request.POST)
        if form.is_valid():
            # Xử lý form rút tiền
            amount = form.cleaned_data['amount']
            bank_account = form.cleaned_data['bank_account']
            withdraw_note = form.cleaned_data['notes']
            
            # Kiểm tra số dư
            if amount > wallet.balance:
                messages.error(request, 'Số dư của bạn không đủ để thực hiện giao dịch này.')
                return redirect('withdraw_money')
            
            # Xử lý tài khoản ngân hàng mới nếu có
            if bank_account == 'new':
                bank_name = form.cleaned_data['new_bank_name']
                other_bank_name = form.cleaned_data['new_other_bank_name']
                account_name = form.cleaned_data['new_account_name']
                account_number = form.cleaned_data['new_account_number']
                branch = form.cleaned_data['new_branch']
                is_default = form.cleaned_data['new_is_default']
                
                if bank_name == 'other' and other_bank_name:
                    display_name = other_bank_name
                else:
                    display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                
                # Tạo tài khoản ngân hàng mới
                bank_account = BankAccount.objects.create(
                    user=request.user,
                    bank_name=bank_name,
                    other_bank_name=other_bank_name,
                    account_name=account_name,
                    account_number=account_number,
                    branch=branch,
                    is_default=is_default
                )
                
                messages.success(request, f'Đã thêm tài khoản {display_name} - {account_number}')
            
            # Tính phí rút tiền (0.5%, tối thiểu 10,000, tối đa 50,000)
            fee = round(float(amount) * 0.005)
            if fee < 10000:
                fee = 10000
            if fee > 50000:
                fee = 50000
            
            net_amount = amount - fee
            
            # Tạo giao dịch rút tiền
            transaction = WalletTransaction.objects.create(
                user=request.user,
                wallet=wallet,
                type='withdraw',
                amount=amount,
                fee=fee,
                net_amount=net_amount,
                status='pending',
                bank_account=bank_account if bank_account != 'new' else bank_account,
                payment_method='bank_transfer',
                transaction_id=f"WIT{uuid.uuid4().hex[:8].upper()}",
                notes=withdraw_note
            )
            
            messages.success(request, f'Yêu cầu rút tiền {amount} VNĐ đã được ghi nhận. Chúng tôi sẽ xử lý trong thời gian sớm nhất.')
            return redirect('wallet')
    else:
        form = WithdrawForm(request.user)
    
    context = {
        'wallet': wallet,
        'bank_accounts': bank_accounts,
        'form': form
    }
    
    return render(request, 'portfolio/withdraw.html', context)

@login_required
def bank_account_list(request):
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'bank_accounts': bank_accounts
    }
    
    return render(request, 'portfolio/bank_account_list.html', context)

@login_required
def add_bank_account(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            bank_account = form.save(commit=False)
            bank_account.user = request.user
            bank_account.save()
            
            bank_name = form.cleaned_data['bank_name']
            if bank_name == 'other':
                display_name = form.cleaned_data['other_bank_name']
            else:
                display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                
            account_number = form.cleaned_data['account_number']
            
            messages.success(request, f'Đã thêm tài khoản {display_name} - {account_number}')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm()
    
    context = {
        'form': form,
        'title': 'Thêm tài khoản ngân hàng'
    }
    
    return render(request, 'portfolio/bank_account_form.html', context)

@login_required
def update_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account)
        if form.is_valid():
            form.save()
            
            bank_name = form.cleaned_data['bank_name']
            if bank_name == 'other':
                display_name = form.cleaned_data['other_bank_name']
            else:
                display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                
            account_number = form.cleaned_data['account_number']
            
            messages.success(request, f'Đã cập nhật tài khoản {display_name} - {account_number}')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm(instance=bank_account)
    
    context = {
        'form': form,
        'bank_account': bank_account,
        'title': 'Cập nhật tài khoản ngân hàng'
    }
    
    return render(request, 'portfolio/bank_account_form.html', context)

@login_required
def delete_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    if request.method == 'POST':
        # Kiểm tra xem có giao dịch đang sử dụng tài khoản này không
        transactions_using_account = WalletTransaction.objects.filter(
            bank_account=bank_account,
            status='pending'
        ).exists()
        
        if transactions_using_account:
            messages.error(request, 'Không thể xóa tài khoản này vì có giao dịch đang xử lý.')
            return redirect('bank_account_list')
        
        # Lưu thông tin để hiển thị thông báo
        bank_name = bank_account.bank_name
        if bank_name == 'other':
            display_name = bank_account.other_bank_name
        else:
            display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
            
        account_number = bank_account.account_number
        
        # Xóa tài khoản
        bank_account.delete()
        
        messages.success(request, f'Đã xóa tài khoản {display_name} - {account_number}')
        return redirect('bank_account_list')
    
    context = {
        'bank_account': bank_account
    }
    
    return render(request, 'portfolio/bank_account_confirm_delete.html', context)

@login_required
def set_default_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    # Đặt tất cả tài khoản khác thành không mặc định
    BankAccount.objects.filter(user=request.user).update(is_default=False)
    
    # Đặt tài khoản hiện tại thành mặc định
    bank_account.is_default = True
    bank_account.save()
    
    bank_name = bank_account.bank_name
    if bank_name == 'other':
        display_name = bank_account.other_bank_name
    else:
        display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
        
    account_number = bank_account.account_number
    
    messages.success(request, f'Đã đặt {display_name} - {account_number} làm tài khoản mặc định')
    
    return redirect('bank_account_list')