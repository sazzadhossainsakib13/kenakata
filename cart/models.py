from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product
from decimal import Decimal
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()}: {self.discount_value})"

    def is_valid(self):
        if not self.is_active:
            return False, "This coupon is not active."
        if self.expiry_date and self.expiry_date < timezone.now():
            return False, "This coupon has expired."
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "This coupon has reached its usage limit."
        return True, "Valid"

    def calculate_discount(self, subtotal):
        valid, msg = self.is_valid()
        if not valid:
            return Decimal('0.00')
        if subtotal < self.min_order_amount:
            return Decimal('0.00')
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / Decimal('100')
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        else:
            return min(self.discount_value, subtotal)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart: {self.user.username}"
        return f"Cart: Guest ({self.session_key})"

    def get_subtotal(self):
        return sum(item.get_total_price() for item in self.items.select_related('product').all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

    def get_coupon_discount(self):
        if self.coupon:
            return self.coupon.calculate_discount(self.get_subtotal())
        return Decimal('0.00')

    def get_delivery_charge(self, zone='outside_dhaka'):
        if not self.items.exists():
            return Decimal('0.00')
        from django.conf import settings
        charges = getattr(settings, 'DELIVERY_CHARGES', {'inside_dhaka': 60, 'outside_dhaka': 120})
        return Decimal(str(charges.get(zone, 120)))

    def get_total(self, zone='outside_dhaka'):
        if not self.items.exists():
            return Decimal('0.00')
        subtotal = self.get_subtotal()
        discount = self.get_coupon_discount()
        delivery = self.get_delivery_charge(zone)
        return max(Decimal('0.00'), subtotal - discount + delivery)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_total_price(self):
        return self.product.selling_price * self.quantity
