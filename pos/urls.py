from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('terminal/', views.terminal, name='terminal'),
    path('search-products/', views.search_products, name='search_products'),
    path('search-customers/', views.search_customers, name='search_customers'),
    path('add-customer/', views.add_customer, name='add_customer'),
    path('complete-sale/', views.complete_sale, name='complete_sale'),
    path('receipt/<str:receipt_number>/', views.receipt_detail, name='receipt_detail'),
    path('sales/', views.sales_history, name='sales_history'),
    path('sales-history/', views.sales_history, name='sales_history_alias'),
    path('sale/<str:receipt_number>/', views.sale_detail, name='sale_detail'),
    path('returns/', views.returns_list, name='returns_list'),
    path('process-return/', views.process_return, name='process_return'),
    path('void-sale/<str:receipt_number>/', views.void_sale, name='void_sale'),
    path('reports/', views.reports, name='reports'),
    path('inventory/', views.inventory, name='inventory'),
    path('adjust-stock/', views.adjust_stock, name='adjust_stock'),
    path('settings/', views.settings_view, name='settings'),
    path('online-orders/', views.online_orders, name='online_orders'),
    path('update-order-status/<str:order_number>/', views.update_order_status, name='update_order_status'),
    path('products/', views.pos_products, name='pos_products'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
]
