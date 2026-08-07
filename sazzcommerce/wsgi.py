import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sazzcommerce.settings')

application = get_wsgi_application()

# Automatic database initialization & fail-safe migration on startup for cloud hosting (Render)
try:
    from django.core.management import call_command
    from catalog.models import Product
    call_command('migrate', interactive=False)
    if Product.objects.count() == 0:
        call_command('seed_data')
except Exception as e:
    print("[KenaKata Boot Notice] DB initialization:", e)

