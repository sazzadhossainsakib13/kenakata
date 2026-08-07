from django.contrib import admin
from .models import UserProfile, Address


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile', 'division', 'created_at']
    search_fields = ['user__username', 'user__email', 'mobile']
    list_filter = ['division']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipient_name', 'label', 'district', 'division', 'is_default']
    list_filter = ['division', 'label', 'is_default']
    search_fields = ['user__username', 'recipient_name', 'mobile', 'district']
