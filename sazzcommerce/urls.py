from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "KenaKata Admin"
admin.site.site_title = "KenaKata"
admin.site.index_title = "KenaKata Marketplace Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('auth/', include('accounts.urls')),
    path('account/', include('dashboard.urls')),
    path('shop/', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('checkout/', include('orders.urls')),
    path('pos/', include('pos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
