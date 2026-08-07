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
    if Product.objects.count() == 0:
        call_command('seed_data')
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@kenakata.com', 'admin1234')
        print("[KenaKata Boot] Default superuser 'admin' created.")
    else:
        # Ensure staff and superuser permissions are intact
        u = User.objects.get(username='admin')
        u.is_staff = True
        u.is_superuser = True
        u.set_password('admin1234')
        u.save()
except Exception as e:
    print("[KenaKata Boot Notice] DB initialization:", e)


