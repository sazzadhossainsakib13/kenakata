from django.contrib import admin
from .models import (
    StoreSettings, POSCustomer, POSSale, POSSaleItem,
    POSReturn, POSReturnItem, InventoryMovement
)


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'phone', 'email', 'low_stock_threshold', 'receipt_prefix', 'updated_at']


@admin.register(POSCustomer)
class POSCustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile', 'email', 'created_at']
    search_fields = ['name', 'mobile', 'email']


class POSSaleItemInline(admin.TabularInline):
    model = POSSaleItem
    extra = 0
    readonly_fields = ['product_name_snapshot', 'sku_snapshot', 'unit_price', 'quantity', 'line_total', 'returned_quantity']


@admin.register(POSSale)
class POSSaleAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'cashier', 'customer', 'subtotal', 'discount_amount', 'total', 'payment_status', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['receipt_number', 'cashier__username', 'customer__name', 'customer__mobile']
    inlines = [POSSaleItemInline]
    readonly_fields = ['receipt_number', 'created_at', 'updated_at']


class POSReturnItemInline(admin.TabularInline):
    model = POSReturnItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price_snapshot', 'refund_amount']


@admin.register(POSReturn)
class POSReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'sale', 'staff', 'total_refund', 'created_at']
    search_fields = ['return_number', 'sale__receipt_number', 'staff__username']
    inlines = [POSReturnItemInline]


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'staff', 'reference_id', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name', 'reference_id', 'reason', 'staff__username']
