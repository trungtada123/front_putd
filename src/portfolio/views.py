from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Portfolio, Asset, Transaction, PortfolioAsset
from .forms import PortfolioForm, AssetForm, TransactionForm, UserRegistrationForm
from django.contrib.auth import login
from decimal import Decimal
from django.http import JsonResponse
from .vnstock_services import get_price_board, get_historical_data
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .utils import get_ai_response

def home(request):
    return render(request, 'portfolio/home.html')

@login_required
def dashboard(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    total_value = sum(p.total_value for p in portfolios)
    total_cost = sum(p.total_cost for p in portfolios)
    total_profit = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
    
    total_assets = PortfolioAsset.objects.filter(
        portfolio__user=request.user,
        quantity__gt=0
    ).count()
    
    monthly_transactions = Transaction.objects.filter(
        portfolio__user=request.user,
        transaction_date__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    
    recent_transactions = Transaction.objects.filter(
        portfolio__user=request.user
    ).order_by('-transaction_date')[:5]

    context = {
        'portfolios': portfolios,
        'total_value': total_value,
        'total_profit': total_profit,
        'total_assets': total_assets,
        'monthly_transactions': monthly_transactions,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'portfolio/dashboard.html', context)

@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/portfolio_list.html', {'portfolios': portfolios})

@login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            
            messages.success(request, 'Danh mục đầu tư đã được tạo thành công!')
            
            # Chuyển hướng đến trang chi tiết danh mục vừa tạo
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm()
    
    return render(request, 'portfolio/portfolio_form.html', {
        'form': form,
        'title': 'Tạo danh mục mới'
    })

@login_required
def portfolio_detail(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    
    # Lấy danh sách tài sản trong danh mục
    portfolio_assets = PortfolioAsset.objects.filter(
        portfolio=portfolio,
        quantity__gt=0
    ).select_related('asset')
    
    # Lấy các giao dịch gần đây
    recent_transactions = Transaction.objects.filter(
        portfolio=portfolio
    ).select_related('asset').order_by('-transaction_date')[:5]
    
    # Tính toán thống kê
    total_invested = sum(pa.quantity * pa.average_price for pa in portfolio_assets)
    total_current_value = sum(pa.current_value for pa in portfolio_assets)
    total_profit_loss = total_current_value - total_invested
    profit_percentage = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
    
    # Phân bổ tài sản theo loại
    asset_allocation = {}
    for pa in portfolio_assets:
        asset_type = pa.asset.get_type_display()
        asset_allocation[asset_type] = asset_allocation.get(asset_type, 0) + pa.current_value
    
    context = {
        'portfolio': portfolio,
        'portfolio_assets': portfolio_assets,
        'recent_transactions': recent_transactions,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_profit_loss': total_profit_loss,
        'profit_percentage': profit_percentage,
        'asset_allocation': asset_allocation,
    }
    
    return render(request, 'portfolio/portfolio_detail.html', context)

@login_required
def portfolio_update(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đầu tư đã được cập nhật!')
            return redirect('portfolio_detail', pk=pk)
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, 'portfolio/portfolio_form.html', {
        'form': form,
        'title': 'Chỉnh sửa danh mục'
    })

@login_required
def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'portfolio/asset_list.html', {'assets': assets})

@login_required
def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tài sản đã được thêm thành công!')
            return redirect('asset_list')
    else:
        form = AssetForm()
    return render(request, 'portfolio/asset_form.html', {'form': form, 'title': 'Thêm tài sản mới'})

@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, 'portfolio/asset_detail.html', {'asset': asset})

@login_required
def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tài sản đã được cập nhật!')
            return redirect('asset_detail', pk=pk)
    else:
        form = AssetForm(instance=asset)
    return render(request, 'portfolio/asset_form.html', {
        'form': form,
        'title': 'Chỉnh sửa tài sản'
    })

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(portfolio__user=request.user)
    
    # Lọc theo danh mục
    portfolio_id = request.GET.get('portfolio')
    if portfolio_id:
        transactions = transactions.filter(portfolio_id=portfolio_id)
    
    # Lọc theo loại giao dịch
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Lọc theo ngày
    from_date = request.GET.get('from_date')
    if from_date:
        transactions = transactions.filter(transaction_date__gte=from_date)
    
    to_date = request.GET.get('to_date')
    if to_date:
        transactions = transactions.filter(transaction_date__lte=to_date)
    
    # Phân trang
    paginator = Paginator(transactions.order_by('-transaction_date'), 10)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'portfolios': Portfolio.objects.filter(user=request.user)
    }
    return render(request, 'portfolio/transaction_list.html', context)

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.total_amount = transaction.quantity * transaction.price
            transaction.save()
            messages.success(request, 'Giao dịch đã được tạo thành công!')
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'portfolio/transaction_form.html', {
        'form': form,
        'title': 'Tạo giao dịch mới'
    })

@login_required
def buy_stock(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.portfolio = portfolio
            transaction.transaction_type = 'buy'
            transaction.transaction_date = timezone.now()
            transaction.save()
            
            messages.success(request, 'Giao dịch mua đã được thực hiện thành công!')
            return redirect('portfolio_detail', pk=portfolio_id)
    else:
        form = TransactionForm(initial={
            'portfolio': portfolio,
            'transaction_type': 'buy',
            'transaction_date': timezone.now()
        })
    
    return render(request, 'portfolio/transaction_form.html', {
        'form': form,
        'title': 'Mua cổ phiếu',
        'portfolio': portfolio
    })

@login_required
def sell_stock(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            asset = form.cleaned_data['asset']
            quantity = form.cleaned_data['quantity']
            
            # Kiểm tra số lượng bán không vượt quá số lượng hiện có
            portfolio_asset = PortfolioAsset.objects.filter(
                portfolio=portfolio,
                asset=asset
            ).first()
            
            if not portfolio_asset or portfolio_asset.quantity < quantity:
                messages.error(request, 'Số lượng bán vượt quá số lượng hiện có!')
                return render(request, 'portfolio/transaction_form.html', {
                    'form': form,
                    'title': 'Bán cổ phiếu',
                    'portfolio': portfolio
                })
            
            transaction = form.save(commit=False)
            transaction.portfolio = portfolio
            transaction.transaction_type = 'sell'
            transaction.transaction_date = timezone.now()
            transaction.save()
            
            messages.success(request, 'Giao dịch bán đã được thực hiện thành công!')
            return redirect('portfolio_detail', pk=portfolio_id)
    else:
        form = TransactionForm(initial={
            'portfolio': portfolio,
            'transaction_type': 'sell',
            'transaction_date': timezone.now()
        })
    
    return render(request, 'portfolio/transaction_form.html', {
        'form': form,
        'title': 'Bán cổ phiếu',
        'portfolio': portfolio
    })

@login_required
def portfolio_transactions(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id, user=request.user)
    transactions = Transaction.objects.filter(portfolio=portfolio).order_by('-transaction_date')
    return render(request, 'portfolio/portfolio_transactions.html', {
        'portfolio': portfolio,
        'transactions': transactions
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'portfolio/register.html', {'form': form})

# ============ MARKET =======
@login_required
def market(request):
    price_board = get_price_board()
    context = {
        "price_board_json": price_board.to_json(orient='split'),
    }
    return render(request, 'portfolio/market.html', context)

def get_historical_data_api(request, stock_code):
    try:
        data = get_historical_data(stock_code)
        return JsonResponse({'data': data.to_dict('records')})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_stock_historical_data(request, symbol):
    try:
        # Lấy dữ liệu lịch sử từ vnstock service
        historical_data = get_historical_data(symbol)
        
        # Chuyển đổi dữ liệu thành định dạng phù hợp cho biểu đồ
        chart_data = []
        for _, row in historical_data.iterrows():
            chart_data.append({
                'time': row['time'].strftime('%Y-%m-%d') if hasattr(row['time'], 'strftime') else str(row['time']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
        
        print(f"Returning data for {symbol}: {len(chart_data)} records") # Debug log
        print(f"Sample data: {chart_data[:1]}") # Debug log để xem mẫu dữ liệu
        return JsonResponse(chart_data, safe=False)
    except Exception as e:
        print(f"Error getting data for {symbol}: {str(e)}") # Debug log
        print(f"Data structure: {historical_data.head()}") if 'historical_data' in locals() else print("No data fetched") # Debug log để xem cấu trúc dữ liệu
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def ai_chat_api(request):
    """
    API endpoint để xử lý các yêu cầu chat với AI
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Tin nhắn không được để trống'
            }, status=400)
        
        # Gọi API AI để nhận phản hồi
        response = get_ai_response(message)
        
        return JsonResponse({
            'success': True,
            'response': response
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dữ liệu JSON không hợp lệ'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)