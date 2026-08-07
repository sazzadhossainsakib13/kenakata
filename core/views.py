from django.shortcuts import render
from django.utils import timezone
from catalog.models import Product, Category, Banner, RecentlyViewed


def home(request):
    """Premium homepage with all sections."""
    # Featured sections
    featured_products = Product.objects.filter(active=True, featured=True).select_related('category', 'brand')[:8]
    flash_sale_products = Product.objects.filter(active=True, flash_sale=True).select_related('category', 'brand')[:8]
    trending_products = Product.objects.filter(active=True, trending=True).select_related('category', 'brand')[:8]
    new_arrivals = Product.objects.filter(active=True, new_arrival=True).select_related('category', 'brand')[:8]
    best_sellers = Product.objects.filter(active=True, best_seller=True).select_related('category', 'brand')[:8]
    top_rated = Product.objects.filter(active=True, average_rating__gte=4.0).order_by('-average_rating').select_related('category', 'brand')[:8]
    budget_deals = Product.objects.filter(active=True, discount_price__isnull=False, discount_price__lte=999).select_related('category', 'brand')[:8]

    # Categories
    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('order', 'name')[:12]

    # Banners
    hero_banners = Banner.objects.filter(is_active=True, banner_type='hero').order_by('order')[:5]
    promo_banners = Banner.objects.filter(is_active=True, banner_type='promotional').order_by('order')[:4]

    # Flash sale end time
    flash_sale_product = flash_sale_products.first()
    flash_sale_end = None
    if flash_sale_product and flash_sale_product.flash_sale_end:
        flash_sale_end = flash_sale_product.flash_sale_end
    else:
        flash_sale_end = timezone.now() + timezone.timedelta(hours=6)

    # Recently viewed
    recently_viewed = []
    if request.user.is_authenticated:
        recently_viewed = RecentlyViewed.objects.filter(
            user=request.user
        ).select_related('product').order_by('-viewed_at')[:8]
    elif request.session.session_key:
        recently_viewed = RecentlyViewed.objects.filter(
            session_key=request.session.session_key
        ).select_related('product').order_by('-viewed_at')[:8]

    context = {
        'featured_products': featured_products,
        'flash_sale_products': flash_sale_products,
        'trending_products': trending_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'top_rated': top_rated,
        'budget_deals': budget_deals,
        'categories': categories,
        'hero_banners': hero_banners,
        'promo_banners': promo_banners,
        'flash_sale_end': flash_sale_end,
        'recently_viewed': recently_viewed,
    }
    return render(request, 'core/home.html', context)


def search(request):
    """Product search with filters."""
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    total_count = 0

    if query:
        from django.db.models import Q
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query),
            active=True
        ).select_related('category', 'brand').distinct()

        # Filters
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        category_slug = request.GET.get('category')
        sort = request.GET.get('sort', 'relevance')

        if min_price:
            try:
                products = products.filter(discount_price__gte=float(min_price)) | products.filter(
                    discount_price__isnull=True, regular_price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                from django.db.models import Q as Q2
                products = products.filter(
                    Q2(discount_price__lte=float(max_price)) |
                    Q2(discount_price__isnull=True, regular_price__lte=float(max_price))
                )
            except ValueError:
                pass
        if category_slug:
            products = products.filter(category__slug=category_slug)

        sort_map = {
            'price_asc': 'discount_price',
            'price_desc': '-discount_price',
            'rating': '-average_rating',
            'newest': '-created_at',
            'popular': '-sold_count',
        }
        if sort in sort_map:
            products = products.order_by(sort_map[sort])

        total_count = products.count()

    from django.core.paginator import Paginator
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True, parent__isnull=True)

    context = {
        'query': query,
        'page_obj': page_obj,
        'total_count': total_count,
        'categories': categories,
    }
    return render(request, 'core/search.html', context)


def track_order(request):
    """Public order tracking by order number and mobile."""
    order = None
    error = None
    if request.method == 'POST':
        order_number = request.POST.get('order_number', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        if order_number and mobile:
            from orders.models import Order
            try:
                order = Order.objects.get(order_number=order_number, mobile=mobile)
            except Order.DoesNotExist:
                error = "No order found with that order number and mobile combination."
        else:
            error = "Please enter both order number and mobile number."
    return render(request, 'core/track_order.html', {'order': order, 'error': error})
