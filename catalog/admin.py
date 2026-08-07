from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductSpecification, Banner


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class ProductSpecInline(admin.TabularInline):
    model = ProductSpecification
    extra = 5


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_editable = ['is_active', 'order']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'regular_price', 'discount_price', 'stock', 'sold_count', 'featured', 'flash_sale', 'active']
    list_filter = ['active', 'featured', 'flash_sale', 'trending', 'new_arrival', 'best_seller', 'category']
    search_fields = ['name', 'sku', 'brand__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['regular_price', 'discount_price', 'stock', 'featured', 'flash_sale', 'active']
    inlines = [ProductImageInline, ProductSpecInline]
    readonly_fields = ['average_rating', 'review_count', 'sold_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'sku', 'category', 'brand')}),
        ('Description', {'fields': ('short_description', 'description')}),
        ('Pricing', {'fields': ('regular_price', 'discount_price')}),
        ('Inventory', {'fields': ('stock',)}),
        ('Media', {'fields': ('image',)}),
        ('Status', {'fields': ('active', 'featured', 'flash_sale', 'flash_sale_end', 'trending', 'new_arrival', 'best_seller')}),
        ('Stats (readonly)', {'fields': ('average_rating', 'review_count', 'sold_count', 'created_at', 'updated_at')}),
    )


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'banner_type', 'is_active', 'order']
    list_filter = ['banner_type', 'is_active']
    list_editable = ['is_active', 'order']
