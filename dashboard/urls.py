from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('addresses/', views.addresses, name='addresses'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('addresses/set-default/<int:pk>/', views.set_default_address, name='set_default_address'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('wishlist/', views.my_wishlist, name='my_wishlist'),
    path('reviews/', views.my_reviews, name='my_reviews'),
    path('reviews/add/<int:product_id>/', views.add_review, name='add_review'),
    path('reviews/delete/<int:pk>/', views.delete_review, name='delete_review'),
]
