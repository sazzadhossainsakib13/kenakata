from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product
from cart.models import Coupon
from decimal import Decimal
import uuid


ORDER_STATUS_CHOICES = [
    ('pending', 'Order Placed'),
    ('confirmed', 'Confirmed'),
    ('packed', 'Packed'),
    ('handed_to_courier', 'Handed to Courier'),
    ('out_for_delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('returned', 'Returned'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('refunded', 'Refunded'),
]

DELIVERY_ZONES = [
    ('inside_dhaka', 'Inside Dhaka'),
    ('outside_dhaka', 'Outside Dhaka'),
]

COURIER_CHOICES = [
    ('pathao', 'Pathao Courier'),
    ('redx', 'RedX'),
    ('steadfast', 'Steadfast'),
    ('paperfly', 'Paperfly'),
    ('marketplace', 'Marketplace Delivery'),
]


def generate_order_number():
    from datetime import datetime
    year = datetime.now().year
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"BD-{year}-{unique_part}"


class Order(models.Model):
    order_number = models.CharField(max_length=30, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # Shipping info
    recipient_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    division = models.CharField(max_length=50)
    district = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=200, blank=True)
    road = models.CharField(max_length=200, blank=True)
    house = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    full_address = models.TextField()
    delivery_instructions = models.TextField(blank=True)
    # Delivery
    delivery_zone = models.CharField(max_length=20, choices=DELIVERY_ZONES, default='outside_dhaka')
    delivery_method = models.CharField(max_length=50, default='Standard Delivery')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('120.00'))
    estimated_delivery = models.CharField(max_length=100, default='3–5 business days')
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    # Payment
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    # Status
    status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='pending')
    # Courier
    courier = models.CharField(max_length=20, choices=COURIER_CHOICES, blank=True)
    tracking_code = models.CharField(max_length=100, blank=True)
    # Timestamps
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number

    def get_status_display_steps(self):
        steps = [
            ('pending', 'Order Placed', 'bi-bag-check'),
            ('confirmed', 'Confirmed', 'bi-check-circle'),
            ('packed', 'Packed', 'bi-box-seam'),
            ('handed_to_courier', 'Handed to Courier', 'bi-truck'),
            ('out_for_delivery', 'Out for Delivery', 'bi-geo-alt'),
            ('delivered', 'Delivered', 'bi-house-check'),
        ]
        current_index = 0
        for i, (status_key, _, _) in enumerate(steps):
            if self.status == status_key:
                current_index = i
                break
        return [(s[0], s[1], s[2], i <= current_index) for i, s in enumerate(steps)]

    def get_short_address(self):
        parts = [self.area, self.district, self.division]
        return ', '.join([p for p in parts if p])

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
            # Ensure uniqueness
            while Order.objects.filter(order_number=self.order_number).exists():
                self.order_number = generate_order_number()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=500)
    product_image = models.CharField(max_length=500, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
