from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from .models import Order, OrderItem
from cart.utils import get_or_create_cart
from catalog.models import Product
from accounts.models import Address, BANGLADESH_DIVISIONS
from decimal import Decimal
import re


def validate_bd_mobile(mobile):
    """Validate Bangladesh mobile number."""
    cleaned = re.sub(r'[\s\-\(\)]', '', mobile)
    pattern = r'^(\+880|880|0)?1[3-9]\d{8}$'
    return bool(re.match(pattern, cleaned))


def normalize_mobile(mobile):
    """Normalize mobile to 01XXXXXXXXX format."""
    cleaned = re.sub(r'[\s\-\(\)]', '', mobile)
    if cleaned.startswith('+880'):
        cleaned = '0' + cleaned[4:]
    elif cleaned.startswith('880'):
        cleaned = '0' + cleaned[3:]
    return cleaned


@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    # Pre-fill address
    default_address = None
    saved_addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    if saved_addresses.exists():
        default_address = saved_addresses.filter(is_default=True).first() or saved_addresses.first()

    if request.method == 'POST':
        # Collect form data
        recipient_name = request.POST.get('recipient_name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        email = request.POST.get('email', '').strip()
        division = request.POST.get('division', '').strip()
        district = request.POST.get('district', '').strip()
        upazila = request.POST.get('upazila', '').strip()
        area = request.POST.get('area', '').strip()
        road = request.POST.get('road', '').strip()
        house = request.POST.get('house', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        delivery_instructions = request.POST.get('delivery_instructions', '').strip()
        save_address = request.POST.get('save_address')

        # Validate
        errors = []
        if not recipient_name:
            errors.append("Recipient name is required.")
        if not mobile:
            errors.append("Mobile number is required.")
        elif not validate_bd_mobile(mobile):
            errors.append("Please enter a valid Bangladesh mobile number (e.g., 01XXXXXXXXX).")
        if not division:
            errors.append("Division is required.")
        if not district:
            errors.append("District is required.")

        if errors:
            for error in errors:
                messages.error(request, error)
            context = _get_checkout_context(cart, items, saved_addresses, default_address)
            context['form_data'] = request.POST
            return render(request, 'orders/checkout.html', context)

        mobile = normalize_mobile(mobile)

        # Determine delivery zone
        delivery_zone = 'inside_dhaka' if division.lower() == 'dhaka' and district.lower() == 'dhaka' else 'outside_dhaka'
        charges = getattr(settings, 'DELIVERY_CHARGES', {'inside_dhaka': 60, 'outside_dhaka': 120})
        shipping_cost = Decimal(str(charges.get(delivery_zone, 120)))
        estimated_delivery = '1–2 business days' if delivery_zone == 'inside_dhaka' else '3–5 business days'

        # Build address string
        full_address_parts = [house, road, area, upazila, district, division]
        full_address = ', '.join([p for p in full_address_parts if p])

        try:
            with transaction.atomic():
                # Re-validate products and prices from DB
                subtotal = Decimal('0.00')
                order_items_data = []

                for item in items:
                    # Fresh product data
                    try:
                        product = Product.objects.select_for_update().get(id=item.product_id, active=True)
                    except Product.DoesNotExist:
                        raise ValueError(f"Product '{item.product.name}' is no longer available.")

                    if product.stock < item.quantity:
                        raise ValueError(f"Insufficient stock for '{product.name}'. Only {product.stock} available.")

                    unit_price = product.selling_price
                    item_subtotal = unit_price * item.quantity
                    subtotal += item_subtotal
                    order_items_data.append({
                        'product': product,
                        'product_name': product.name,
                        'product_image': product.get_main_image_url(),
                        'unit_price': unit_price,
                        'quantity': item.quantity,
                        'subtotal': item_subtotal,
                    })

                # Re-validate coupon
                discount_amount = Decimal('0.00')
                coupon = cart.coupon
                coupon_code = ''
                if coupon:
                    valid, msg = coupon.is_valid()
                    if valid and subtotal >= coupon.min_order_amount:
                        discount_amount = coupon.calculate_discount(subtotal)
                        coupon_code = coupon.code
                    else:
                        coupon = None

                total = subtotal - discount_amount + shipping_cost

                # Create order
                order = Order.objects.create(
                    user=request.user,
                    recipient_name=recipient_name,
                    mobile=mobile,
                    email=email or request.user.email,
                    division=division,
                    district=district,
                    upazila=upazila,
                    area=area,
                    road=road,
                    house=house,
                    postal_code=postal_code,
                    full_address=full_address,
                    delivery_instructions=delivery_instructions,
                    delivery_zone=delivery_zone,
                    shipping_cost=shipping_cost,
                    estimated_delivery=estimated_delivery,
                    subtotal=subtotal,
                    coupon=coupon,
                    coupon_code=coupon_code,
                    discount_amount=discount_amount,
                    total=total,
                    payment_method='Cash on Delivery',
                    payment_status='pending',
                    status='pending',
                )

                # Create order items, deduct stock, and log inventory movement
                from pos.models import InventoryMovement
                for item_data in order_items_data:
                    OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],
                        product_name=item_data['product_name'],
                        product_image=item_data['product_image'],
                        unit_price=item_data['unit_price'],
                        quantity=item_data['quantity'],
                        subtotal=item_data['subtotal'],
                    )
                    prev_stock = item_data['product'].stock
                    item_data['product'].stock -= item_data['quantity']
                    item_data['product'].sold_count += item_data['quantity']
                    item_data['product'].save(update_fields=['stock', 'sold_count'])

                    InventoryMovement.objects.create(
                        product=item_data['product'],
                        movement_type='ONLINE_SALE',
                        quantity=-item_data['quantity'],
                        previous_stock=prev_stock,
                        new_stock=item_data['product'].stock,
                        reference_type='Order',
                        reference_id=order.order_number,
                        staff=request.user if request.user.is_authenticated else None,
                        reason=f"Online e-commerce sale ({order.order_number})"
                    )

                # Increment coupon usage
                if coupon:
                    coupon.used_count += 1
                    coupon.save(update_fields=['used_count'])

                # Save address if requested
                if save_address:
                    Address.objects.create(
                        user=request.user,
                        label='home',
                        recipient_name=recipient_name,
                        mobile=mobile,
                        email=email,
                        division=division,
                        district=district,
                        upazila=upazila,
                        area=area,
                        road=road,
                        house=house,
                        postal_code=postal_code,
                        full_address=full_address,
                        delivery_instructions=delivery_instructions,
                    )

                # Clear cart
                cart.items.all().delete()
                cart.coupon = None
                cart.save()

                return redirect('orders:order_success', order_number=order.order_number)

        except ValueError as e:
            context = _get_checkout_context(request, cart, items, saved_addresses, default_address)
            context['form_data'] = request.POST
            return render(request, 'orders/checkout.html', context)
        except Exception as e:
            messages.error(request, "An error occurred while placing your order. Please try again.")

    context = _get_checkout_context(request, cart, items, saved_addresses, default_address)
    return render(request, 'orders/checkout.html', context)


def _get_checkout_context(request, cart, items, saved_addresses, default_address):
    form_data = {}
    if default_address:
        form_data = {
            'recipient_name': default_address.recipient_name,
            'mobile': default_address.mobile,
            'email': default_address.email or (request.user.email if request.user.is_authenticated else ''),
            'division': default_address.division,
            'district': default_address.district,
            'upazila': default_address.upazila,
            'area': default_address.area,
            'road': default_address.road,
            'house': default_address.house,
            'postal_code': default_address.postal_code,
        }
    elif request.user.is_authenticated:
        profile_mobile = ''
        profile_division = ''
        if hasattr(request.user, 'profile'):
            profile_mobile = request.user.profile.mobile or ''
            profile_division = request.user.profile.division or ''
        form_data = {
            'recipient_name': request.user.get_full_name() or request.user.username,
            'mobile': profile_mobile,
            'email': request.user.email or '',
            'division': profile_division,
            'district': '',
            'upazila': '',
            'area': '',
            'road': '',
            'house': '',
            'postal_code': '',
        }

    return {
        'cart': cart,
        'items': items,
        'saved_addresses': saved_addresses,
        'default_address': default_address,
        'divisions': BANGLADESH_DIVISIONS,
        'subtotal': cart.get_subtotal(),
        'coupon_discount': cart.get_coupon_discount(),
        'delivery_charge': cart.get_delivery_charge(),
        'form_data': form_data,
    }


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    items = order.items.all()
    tracking_steps = order.get_status_display_steps()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items,
        'tracking_steps': tracking_steps,
    })
