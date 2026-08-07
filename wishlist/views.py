from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Wishlist, WishlistItem
from catalog.models import Product
from cart.utils import get_or_create_cart
from cart.models import CartItem


@login_required
def wishlist_detail(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product__category').order_by('-added_at')
    return render(request, 'wishlist/wishlist_detail.html', {'wishlist': wishlist, 'items': items})


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

    msg = f"'{product.name}' added to wishlist!" if created else f"'{product.name}' is already in your wishlist."
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'created': created, 'message': msg, 'wishlist_count': wishlist.get_item_count()})
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.items.filter(product=product).delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f"Removed from wishlist.", 'wishlist_count': wishlist.get_item_count()})
    messages.success(request, f"'{product.name}' removed from wishlist.")
    return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist_detail'))


@login_required
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if product.is_in_stock:
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity = min(cart_item.quantity + 1, product.stock)
            cart_item.save()
        wishlist.items.filter(product=product).delete()
        messages.success(request, f"'{product.name}' moved to cart!")
    else:
        messages.error(request, f"'{product.name}' is out of stock.")

    return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist_detail'))
