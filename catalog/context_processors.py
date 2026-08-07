from .models import Category


def catalog_context(request):
    """Add nav categories to all templates."""
    try:
        nav_categories = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).order_by('order', 'name')[:12]
    except Exception:
        nav_categories = []
    return {'nav_categories': nav_categories}
