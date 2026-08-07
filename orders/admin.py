from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'unit_price', 'quantity', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'recipient_name', 'mobile', 'district', 'total', 'payment_status', 'status', 'courier', 'created_at']
    list_filter = ['status', 'payment_status', 'delivery_zone', 'courier', 'created_at']
    search_fields = ['order_number', 'recipient_name', 'mobile', 'email']
    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 'updated_at']
    list_editable = ['status', 'payment_status', 'courier']
    ordering = ['-created_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'user', 'status', 'notes')}),
        ('Contact', {'fields': ('recipient_name', 'mobile', 'email')}),
        ('Delivery Address', {'fields': ('division', 'district', 'upazila', 'area', 'road', 'house', 'postal_code', 'full_address', 'delivery_instructions')}),
        ('Delivery', {'fields': ('delivery_zone', 'delivery_method', 'shipping_cost', 'estimated_delivery')}),
        ('Pricing', {'fields': ('subtotal', 'coupon_code', 'discount_amount', 'total')}),
        ('Payment', {'fields': ('payment_method', 'payment_status')}),
        ('Courier', {'fields': ('courier', 'tracking_code')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
