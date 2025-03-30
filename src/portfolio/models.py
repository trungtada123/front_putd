from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.utils import timezone

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username'])
        ]

class Portfolio(models.Model):
    RISK_CHOICES = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    description = models.TextField(blank=True, verbose_name="Mô tả")
    investment_goal = models.CharField(max_length=200, blank=True, verbose_name="Mục tiêu đầu tư")
    target_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Giá trị mục tiêu")
    risk_tolerance = models.CharField(max_length=10, choices=RISK_CHOICES, default='medium', verbose_name="Mức độ rủi ro")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'])
        ]
        verbose_name = "Danh mục đầu tư"
        verbose_name_plural = "Danh mục đầu tư"

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return sum(asset.current_value for asset in self.portfolioasset_set.all())

    @property
    def total_cost(self):
        return sum(asset.quantity * asset.average_price for asset in self.portfolioasset_set.all())

    @property
    def profit_loss(self):
        return self.total_value - self.total_cost

    @property
    def profit_loss_percentage(self):
        if self.total_cost == 0:
            return 0
        return (self.profit_loss / self.total_cost) * 100

    @property
    def target_progress(self):
        if self.target_value == 0:
            return 0
        return (self.total_value / self.target_value) * 100

class Asset(models.Model):
    ASSET_TYPES = [
        ('stock', 'Cổ phiếu'),
        ('bond', 'Trái phiếu'),
        ('fund', 'Quỹ đầu tư'),
    ]
    
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    sector = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    current_price = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['type']),
            models.Index(fields=['sector'])
        ]

class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    average_price = models.DecimalField(max_digits=15, decimal_places=2)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['portfolio']),
            models.Index(fields=['asset'])
        ]

    def update_values(self):
        """Cập nhật giá trị và lãi/lỗ của tài sản"""
        self.current_value = self.quantity * self.asset.current_price
        self.profit_loss = self.current_value - (self.quantity * self.average_price)
        self.save()

    def recalculate_average_price(self):
        """Tính lại giá trung bình sau khi có giao dịch mới"""
        transactions = Transaction.objects.filter(
            portfolio=self.portfolio,
            asset=self.asset,
            transaction_type='buy'
        )
        total_quantity = sum(t.quantity for t in transactions)
        total_cost = sum(t.quantity * t.price for t in transactions)
        
        if total_quantity > 0:
            self.average_price = total_cost / total_quantity
        self.save()

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('buy', 'Mua'),
        ('sell', 'Bán'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['portfolio']),
            models.Index(fields=['asset']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['transaction_type'])
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.asset.symbol}"

    def save(self, *args, **kwargs):
        # Tính tổng giá trị giao dịch
        if not self.total_amount:
            self.total_amount = self.quantity * self.price

        # Lưu giao dịch
        super().save(*args, **kwargs)

        # Cập nhật PortfolioAsset
        portfolio_asset, created = PortfolioAsset.objects.get_or_create(
            portfolio=self.portfolio,
            asset=self.asset,
            defaults={
                'quantity': 0,
                'average_price': 0,
                'current_value': 0,
                'profit_loss': 0
            }
        )

        # Cập nhật số lượng
        if self.transaction_type == 'buy':
            portfolio_asset.quantity += self.quantity
        else:  # sell
            portfolio_asset.quantity -= self.quantity

        # Tính lại giá trung bình nếu là giao dịch mua
        if self.transaction_type == 'buy':
            portfolio_asset.recalculate_average_price()

        # Cập nhật giá trị hiện tại và lãi/lỗ
        portfolio_asset.update_values() 