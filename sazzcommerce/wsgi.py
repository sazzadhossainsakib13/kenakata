import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sazzcommerce.settings')

application = get_wsgi_application()

# Automatic database initialization & fail-safe migration on startup for cloud hosting (Render)
try:
    from django.core.management import call_command
    from django.contrib.auth.models import User
    from catalog.models import Product
    call_command('migrate', interactive=False)
    if Product.objects.count() == 0 or User.objects.count() == 0:
        call_command('seed_data')
    
    # Optional superuser initialization from environment variables only (never hardcoded in code)
    admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@kenakata.com')
    if admin_password and not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(admin_username, admin_email, admin_password)
        print(f"[KenaKata Boot] Superuser '{admin_username}' created from environment variables.")
except Exception as e:
    print("[KenaKata Boot Notice] DB initialization:", e)


