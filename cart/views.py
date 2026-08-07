from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem, Coupon
from .utils import get_or_create_cart
from catalog.models import Product
from django.utils import timezone


def cart_detail(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'items': items,
        'delivery_charge': cart.get_delivery_charge(),
        'coupon_discount': cart.get_coupon_discount(),
    }
    return render(request, 'cart/cart_detail.html', context)


def cart_add(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, active=True)
        quantity = int(request.POST.get('quantity', 1))

        if quantity < 1:
            quantity = 1
        if quantity > product.stock:
            quantity = product.stock

        if product.stock < 1:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Product is out of stock.'})
            messages.error(request, f"'{product.name}' is out of stock.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            new_qty = cart_item.quantity + quantity
            cart_item.quantity = min(new_qty, product.stock)
            cart_item.save()

        msg = f"'{product.name}' added to cart!"
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': msg,
                'cart_count': cart.get_item_count()
            })
        messages.success(request, msg)
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('/')


def cart_remove(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = item.product.name
    item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"'{product_name}' removed from cart.",
            'cart_count': cart.get_item_count(),
            'subtotal': str(cart.get_subtotal()),
        })
    messages.success(request, f"'{product_name}' removed from cart.")
    return redirect('cart:cart_detail')


def cart_update(request, item_id):
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.POST.get('quantity', 1))

        if quantity < 1:
            item.delete()
        else:
            item.quantity = min(quantity, item.product.stock)
            item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'item_total': str(item.get_total_price()) if quantity >= 1 else '0',
                'cart_subtotal': str(cart.get_subtotal()),
                'cart_count': cart.get_item_count(),
            })
    return redirect('cart:cart_detail')


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        cart = get_or_create_cart(request)

        try:
            coupon = Coupon.objects.get(code=code)
            valid, message = coupon.is_valid()
            if valid:
                subtotal = cart.get_subtotal()
                if subtotal < coupon.min_order_amount:
                    messages.error(request, f"Minimum order amount of ৳{coupon.min_order_amount} required for this coupon.")
                else:
                    cart.coupon = coupon
                    cart.save()
                    discount = coupon.calculate_discount(subtotal)
                    messages.success(request, f"Coupon '{code}' applied! You saved ৳{discount:.0f}.")
            else:
                messages.error(request, message)
        except Coupon.DoesNotExist:
            messages.error(request, f"Coupon '{code}' is not valid.")

    return redirect('cart:cart_detail')


def remove_coupon(request):
    cart = get_or_create_cart(request)
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon removed.")
    return redirect('cart:cart_detail')
