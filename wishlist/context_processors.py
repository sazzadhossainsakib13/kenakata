from .models import Wishlist


def wishlist_context(request):
    """Add wishlist items & count to all template contexts."""
    wishlist_count = 0
    wishlist_product_ids = []
    try:
        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(user=request.user).first()
            if wishlist:
                wishlist_product_ids = list(wishlist.items.values_list('product_id', flat=True))
                wishlist_count = len(wishlist_product_ids)
    except Exception:
        pass
    return {
        'wishlist_count': wishlist_count,
        'wishlist_product_ids': wishlist_product_ids,
    }
