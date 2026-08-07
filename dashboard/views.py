from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from accounts.models import UserProfile, Address, BANGLADESH_DIVISIONS
from orders.models import Order
from wishlist.models import Wishlist, WishlistItem
from reviews.models import Review
from catalog.models import Product


@login_required
def dashboard_home(request):
    orders = Order.objects.filter(user=request.user)
    total_orders = orders.count()
    processing = orders.filter(status__in=['pending', 'confirmed', 'packed', 'handed_to_courier', 'out_for_delivery']).count()
    delivered = orders.filter(status='delivered').count()
    wishlist_count = 0
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist_count = wishlist.get_item_count()
    except Wishlist.DoesNotExist:
        pass

    recent_orders = orders.prefetch_related('items').order_by('-created_at')[:5]
    return render(request, 'dashboard/home.html', {
        'total_orders': total_orders,
        'processing': processing,
        'delivered': delivered,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'dashboard/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    tracking_steps = order.get_status_display_steps()
    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'tracking_steps': tracking_steps,
    })


@login_required
def addresses(request):
    address_list = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    return render(request, 'dashboard/addresses.html', {'address_list': address_list})


@login_required
def add_address(request):
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            label=request.POST.get('label', 'home'),
            recipient_name=request.POST.get('recipient_name', ''),
            mobile=request.POST.get('mobile', ''),
            email=request.POST.get('email', ''),
            division=request.POST.get('division', ''),
            district=request.POST.get('district', ''),
            upazila=request.POST.get('upazila', ''),
            area=request.POST.get('area', ''),
            road=request.POST.get('road', ''),
            house=request.POST.get('house', ''),
            postal_code=request.POST.get('postal_code', ''),
            full_address=request.POST.get('full_address', ''),
            delivery_instructions=request.POST.get('delivery_instructions', ''),
            is_default=bool(request.POST.get('is_default')),
        )
        messages.success(request, "Address added successfully.")
        return redirect('dashboard:addresses')
    return render(request, 'dashboard/address_form.html', {'divisions': BANGLADESH_DIVISIONS, 'action': 'add'})


@login_required
def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.label = request.POST.get('label', 'home')
        address.recipient_name = request.POST.get('recipient_name', '')
        address.mobile = request.POST.get('mobile', '')
        address.email = request.POST.get('email', '')
        address.division = request.POST.get('division', '')
        address.district = request.POST.get('district', '')
        address.upazila = request.POST.get('upazila', '')
        address.area = request.POST.get('area', '')
        address.road = request.POST.get('road', '')
        address.house = request.POST.get('house', '')
        address.postal_code = request.POST.get('postal_code', '')
        address.full_address = request.POST.get('full_address', '')
        address.delivery_instructions = request.POST.get('delivery_instructions', '')
        address.is_default = bool(request.POST.get('is_default'))
        address.save()
        messages.success(request, "Address updated successfully.")
        return redirect('dashboard:addresses')
    return render(request, 'dashboard/address_form.html', {
        'address': address,
        'divisions': BANGLADESH_DIVISIONS,
        'action': 'edit'
    })


@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address deleted.")
    return redirect('dashboard:addresses')


@login_required
def set_default_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, "Default address updated.")
    return redirect('dashboard:addresses')


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        user.save()
        profile_obj.mobile = request.POST.get('mobile', '')
        profile_obj.division = request.POST.get('division', '')
        if request.FILES.get('avatar'):
            profile_obj.avatar = request.FILES['avatar']
        profile_obj.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard:profile')
    return render(request, 'dashboard/profile.html', {
        'profile': profile_obj,
        'divisions': BANGLADESH_DIVISIONS,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if not request.user.check_password(current):
            messages.error(request, "Current password is incorrect.")
        elif len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters.")
        elif new_password != confirm:
            messages.error(request, "New passwords do not match.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully.")
            return redirect('dashboard:profile')
    return render(request, 'dashboard/change_password.html')


@login_required
def my_wishlist(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product').order_by('-added_at')
    return render(request, 'dashboard/my_wishlist.html', {'wishlist': wishlist, 'items': items})


@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related('product').order_by('-created_at')
    return render(request, 'dashboard/my_reviews.html', {'reviews': reviews})


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)

    # Check if already reviewed
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.info(request, "You have already reviewed this product.")
        return redirect('catalog:product_detail', slug=product.slug)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')

        if not rating or not comment:
            messages.error(request, "Rating and comment are required.")
            return redirect('catalog:product_detail', slug=product.slug)

        # Check verified purchase
        is_verified = Order.objects.filter(
            user=request.user,
            status='delivered',
            items__product=product
        ).exists()

        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            title=title,
            comment=comment,
            is_verified_purchase=is_verified,
        )

        # Update product rating
        from django.db.models import Avg
        agg = Review.objects.filter(product=product, is_approved=True).aggregate(avg=Avg('rating'))
        product.average_rating = agg['avg'] or 0
        product.review_count = Review.objects.filter(product=product, is_approved=True).count()
        product.save(update_fields=['average_rating', 'review_count'])

        messages.success(request, "Thank you for your review!")
        return redirect('catalog:product_detail', slug=product.slug)

    return redirect('catalog:product_detail', slug=product.slug)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    product = review.product
    review.delete()

    # Update product rating
    from django.db.models import Avg
    agg = Review.objects.filter(product=product, is_approved=True).aggregate(avg=Avg('rating'))
    product.average_rating = agg['avg'] or 0
    product.review_count = Review.objects.filter(product=product, is_approved=True).count()
    product.save(update_fields=['average_rating', 'review_count'])

    messages.success(request, "Review deleted.")
    return redirect('dashboard:my_reviews')
