from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<str:order_number>/', views.order_success, name='order_success'),
    path('order-confirmation/<str:order_number>/', views.order_success, name='order_confirmation'),
    path('confirmation/<str:order_number>/', views.order_success, name='confirmation'),
    path('receipt/<str:order_number>/', views.order_detail, name='order_receipt_page'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
]
