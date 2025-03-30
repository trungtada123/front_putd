from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolios/create/', views.portfolio_create, name='portfolio_create'),
    path('portfolios/<int:pk>/', views.portfolio_detail, name='portfolio_detail'),
    path('portfolios/<int:pk>/update/', views.portfolio_update, name='portfolio_update'),
    path('portfolios/<int:portfolio_id>/buy/', views.buy_stock, name='buy_stock'),
    path('portfolios/<int:portfolio_id>/sell/', views.sell_stock, name='sell_stock'),
    path('portfolios/<int:portfolio_id>/transactions/', views.portfolio_transactions, name='portfolio_transactions'),
    
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/update/', views.asset_update, name='asset_update'),
    
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='portfolio/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] 