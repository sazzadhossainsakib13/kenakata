from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Brand, RecentlyViewed
from decimal import Decimal


def product_list(request):
    """Full shop with filters and sorting."""
    products = Product.objects.filter(active=True).select_related('category', 'brand')

    # Filter by category
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        # Include subcategories
        category_ids = [selected_category.id] + list(selected_category.children.values_list('id', flat=True))
        products = products.filter(category_id__in=category_ids)

    # Filter by brand
    brand_slug = request.GET.get('brand')
    selected_brand = None
    if brand_slug:
        selected_brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
        products = products.filter(brand=selected_brand)

    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(
                Q(discount_price__gte=Decimal(min_price)) | Q(discount_price__isnull=True, regular_price__gte=Decimal(min_price))
            )
        except Exception:
            pass
    if max_price:
        try:
            products = products.filter(
                Q(discount_price__lte=Decimal(max_price)) | Q(discount_price__isnull=True, regular_price__lte=Decimal(max_price))
            )
        except Exception:
            pass

    # Rating filter
    min_rating = request.GET.get('rating')
    if min_rating:
        try:
            products = products.filter(average_rating__gte=Decimal(min_rating))
        except Exception:
            pass

    # Discount filter
    on_sale = request.GET.get('on_sale')
    if on_sale:
        products = products.filter(discount_price__isnull=False)

    # Availability filter
    in_stock = request.GET.get('in_stock')
    if in_stock:
        products = products.filter(stock__gt=0)

    # Sorting
    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest': '-created_at',
        'popular': '-sold_count',
        'price_asc': 'discount_price',
        'price_desc': '-discount_price',
        'rating': '-average_rating',
        'discount': '-discount_price',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    total_count = products.count()
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('order', 'name')
    brands = Brand.objects.filter(is_active=True).order_by('name')[:20]

    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'sort': sort,
    }
    return render(request, 'catalog/product_list.html', context)


def category_detail(request, slug):
    """Category-specific product listing."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    category_ids = [category.id] + list(category.children.values_list('id', flat=True))
    products = Product.objects.filter(active=True, category_id__in=category_ids).select_related('category', 'brand')

    # Sorting
    sort = request.GET.get('sort', 'popular')
    sort_map = {
        'newest': '-created_at',
        'popular': '-sold_count',
        'price_asc': 'discount_price',
        'price_desc': '-discount_price',
        'rating': '-average_rating',
    }
    products = products.order_by(sort_map.get(sort, '-sold_count'))

    total_count = products.count()
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    subcategories = category.children.filter(is_active=True)

    context = {
        'category': category,
        'subcategories': subcategories,
        'page_obj': page_obj,
        'total_count': total_count,
        'sort': sort,
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, slug):
    """Premium product detail page."""
    product = get_object_or_404(Product, slug=slug, active=True)
    images = product.images.all().order_by('order')
    specifications = product.specifications.all().order_by('order')

    # Reviews
    from reviews.models import Review
    reviews = Review.objects.filter(product=product, is_approved=True).select_related('user').order_by('-created_at')
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    # Rating distribution
    rating_dist = {}
    for i in range(1, 6):
        count = reviews.filter(rating=i).count()
        rating_dist[i] = {'count': count, 'percent': (count / reviews.count() * 100) if reviews.count() > 0 else 0}

    # Related products
    related_products = Product.objects.filter(
        active=True,
        category=product.category
    ).exclude(id=product.id).select_related('category', 'brand')[:8]

    # Track recently viewed
    _track_recently_viewed(request, product)

    # Check wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        from wishlist.models import Wishlist
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            in_wishlist = wishlist.items.filter(product=product).exists()
        except Wishlist.DoesNotExist:
            pass

    context = {
        'product': product,
        'images': images,
        'specifications': specifications,
        'reviews': reviews,
        'user_review': user_review,
        'rating_dist': rating_dist,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'catalog/product_detail.html', context)


def _track_recently_viewed(request, product):
    """Track product as recently viewed."""
    try:
        if request.user.is_authenticated:
            RecentlyViewed.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={'viewed_at': __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()}
            )
        else:
            if not request.session.session_key:
                request.session.create()
            RecentlyViewed.objects.update_or_create(
                session_key=request.session.session_key,
                product=product,
                defaults={}
            )
    except Exception:
        pass
