from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product
from decimal import Decimal
import uuid


class StoreSettings(models.Model):
    """Dynamic Store & POS Settings."""
    store_name = models.CharField(max_length=200, default='KenaKata Retail & Marketplace')
    store_logo = models.ImageField(upload_to='store/', blank=True, null=True)
    phone = models.CharField(max_length=50, default='01700-000000')
    email = models.EmailField(default='support@kenakata.com')
    address = models.TextField(default='Level 4, Corporate Tower, Gulshan-2, Dhaka-1212, Bangladesh')
    receipt_prefix = models.CharField(max_length=20, default='POS-2026')
    receipt_footer = models.TextField(default='Thank you for shopping at KenaKata! Please visit again. Returns allowed within 7 days with original receipt.')
    currency_symbol = models.CharField(max_length=10, default='৳')
    low_stock_threshold = models.PositiveIntegerField(default=5)
    allow_pos_discount = models.BooleanField(default=True)
    max_cashier_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    max_seller_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'))
    max_admin_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('30.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Store Settings'

    def __str__(self):
        return self.store_name

    @classmethod
    def get_settings(cls):
        settings_obj, _ = cls.objects.get_or_create(id=1)
        return settings_obj


class POSCustomer(models.Model):
    """Walk-in or registered POS Customer."""
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15, unique=True, db_index=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.mobile})"


STATUS_CHOICES = [
    ('completed', 'Completed'),
    ('partially_returned', 'Partially Returned'),
    ('returned', 'Fully Returned'),
    ('voided', 'Voided'),
]

DISCOUNT_TYPE_CHOICES = [
    ('none', 'None'),
    ('percentage', 'Percentage (%)'),
    ('fixed', 'Fixed Amount (৳)'),
]


def generate_receipt_number():
    from datetime import datetime
    year = datetime.now().year
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"POS-{year}-{unique_part}"


class POSSale(models.Model):
    """POS Transaction Header."""
    receipt_number = models.CharField(max_length=40, unique=True, db_index=True)
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pos_sales')
    customer = models.ForeignKey(POSCustomer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    customer_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pos_purchases')
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='none')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    cash_received = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    change_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_method = models.CharField(max_length=20, default='CASH')
    payment_status = models.CharField(max_length=20, default='PAID')
    
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.receipt_number} — ৳{self.total}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            store_settings = StoreSettings.get_settings()
            prefix = store_settings.receipt_prefix or 'POS-2026'
            self.receipt_number = f"{prefix}-{uuid.uuid4().hex[:6].upper()}"
            while POSSale.objects.filter(receipt_number=self.receipt_number).exists():
                self.receipt_number = f"{prefix}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class POSSaleItem(models.Model):
    """Line item snapshot in a POS Sale."""
    sale = models.ForeignKey(POSSale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='pos_sale_items')
    product_name_snapshot = models.CharField(max_length=500)
    sku_snapshot = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    returned_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quantity}x {self.product_name_snapshot} ({self.sale.receipt_number})"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    @property
    def remaining_returnable_quantity(self):
        return max(0, self.quantity - self.returned_quantity)


def generate_return_number():
    return f"RET-{uuid.uuid4().hex[:8].upper()}"


class POSReturn(models.Model):
    """POS Return Header."""
    return_number = models.CharField(max_length=40, unique=True, db_index=True)
    sale = models.ForeignKey(POSSale, on_delete=models.CASCADE, related_name='returns')
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_returns')
    reason = models.TextField()
    total_refund = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.return_number} (Ref: {self.sale.receipt_number})"

    def save(self, *args, **kwargs):
        if not self.return_number:
            self.return_number = generate_return_number()
            while POSReturn.objects.filter(return_number=self.return_number).exists():
                self.return_number = generate_return_number()
        super().save(*args, **kwargs)


class POSReturnItem(models.Model):
    """Line item in a POS Return."""
    return_obj = models.ForeignKey(POSReturn, on_delete=models.CASCADE, related_name='items')
    sale_item = models.ForeignKey(POSSaleItem, on_delete=models.CASCADE, related_name='return_records')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.refund_amount = self.unit_price_snapshot * self.quantity
        super().save(*args, **kwargs)


MOVEMENT_TYPES = [
    ('ONLINE_SALE', 'Online E-commerce Order'),
    ('POS_SALE', 'POS Terminal Sale'),
    ('POS_RETURN', 'POS Return Restock'),
    ('ORDER_CANCEL', 'Online Order Cancelled'),
    ('RESTOCK', 'Supplier Restock'),
    ('MANUAL_ADJUSTMENT', 'Manual Stock Adjustment'),
]


class InventoryMovement(models.Model):
    """Audit ledger for all inventory adjustments."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_movements')
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(help_text="Positive for addition, negative for deduction")
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} | {self.get_movement_type_display()} | Qty: {self.quantity} ({self.previous_stock} -> {self.new_stock})"
