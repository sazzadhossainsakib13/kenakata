from .models import Cart


def cart_context(request):
    """Add cart data to all template contexts."""
    cart = None
    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.prefetch_related('items__product').filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.prefetch_related('items__product').filter(session_key=session_key).first()
        if cart:
            cart_count = cart.get_item_count()
    except Exception:
        pass
    return {'cart': cart, 'cart_count': cart_count}
