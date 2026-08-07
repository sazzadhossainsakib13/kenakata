from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count, Avg, F, Q, DecimalField, ExpressionWrapper
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal
import json, re

from .models import (
    StoreSettings, POSCustomer, POSSale, POSSaleItem,
    POSReturn, POSReturnItem, InventoryMovement
)
from catalog.models import Product, Category, Brand
from django.contrib.auth.models import User


def pos_staff_required(view_func):
    """Ensure user is logged in and is a staff member or superuser."""
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access the POS system.")
            return redirect(f'/auth/login/?next={request.path}')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Access denied. Only authorized staff members can access the POS system.")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped


def validate_bd_mobile(mobile):
    cleaned = re.sub(r'[\s\-\(\)]', '', mobile)
    pattern = r'^(\+880|880|0)?1[3-9]\d{8}$'
    return bool(re.match(pattern, cleaned))


@pos_staff_required
def dashboard(request):
    """Dynamic POS & E-Commerce Web Admin Dashboard."""
    from orders.models import Order, OrderItem
    settings_obj = StoreSettings.get_settings()
    today = timezone.now().date()
    start_of_today = timezone.make_aware(datetime.combine(today, time.min))
    end_of_today = timezone.make_aware(datetime.combine(today, time.max))

    # All-time Sales Total (POS + Online Web Orders)
    pos_all_time_total = POSSale.objects.filter(status__in=['completed', 'partially_returned']).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    online_all_time_total = Order.objects.filter(status='delivered').aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_sales_all_time = pos_all_time_total + online_all_time_total

    # Sales today (POS + Online Web Orders)
    today_pos_qs = POSSale.objects.filter(created_at__range=(start_of_today, end_of_today), status__in=['completed', 'partially_returned'])
    today_online_qs = Order.objects.filter(created_at__range=(start_of_today, end_of_today))

    today_pos_total = today_pos_qs.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    today_online_total = Order.objects.filter(created_at__range=(start_of_today, end_of_today), status='delivered').aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    today_sales_total = today_pos_total + today_online_total

    today_transactions_count = today_pos_qs.count() + today_online_qs.count()
    
    today_pos_items = POSSaleItem.objects.filter(sale__in=today_pos_qs).aggregate(total=Sum('quantity'))['total'] or 0
    today_online_items = OrderItem.objects.filter(order__in=today_online_qs).aggregate(total=Sum('quantity'))['total'] or 0
    today_items_sold = today_pos_items + today_online_items

    today_avg_sale = (today_sales_total / today_transactions_count) if today_transactions_count > 0 else Decimal('0.00')
    today_cash_collected = today_pos_qs.aggregate(total=Sum('cash_received'))['total'] or Decimal('0.00')

    # Inventory stats
    total_products = Product.objects.count()
    active_products = Product.objects.filter(active=True).count()
    low_threshold = settings_obj.low_stock_threshold
    low_stock_products = Product.objects.filter(active=True, stock__gt=0, stock__lte=low_threshold)
    low_stock_count = low_stock_products.count()
    out_of_stock_count = Product.objects.filter(active=True, stock=0).count()

    # Returns today
    returns_today_count = POSReturn.objects.filter(created_at__range=(start_of_today, end_of_today)).count()

    # Online E-commerce Orders Status Breakdown
    online_orders_qs = Order.objects.all()
    total_online_orders = online_orders_qs.count()
    online_pending_count = online_orders_qs.filter(status='pending').count() # On Hold
    online_confirmed_count = online_orders_qs.filter(status='confirmed').count()
    online_processing_count = online_orders_qs.filter(status__in=['packed', 'handed_to_courier', 'out_for_delivery']).count()
    online_delivered_count = online_orders_qs.filter(status='delivered').count() # Completed
    online_cancelled_count = online_orders_qs.filter(status__in=['cancelled', 'returned']).count()
    online_revenue = online_orders_qs.filter(status='delivered').aggregate(s=Sum('total'))['s'] or Decimal('0.00')

    # POS Sales Status Breakdown
    completed_pos_sales = POSSale.objects.filter(status='completed').count()
    partially_returned_pos_sales = POSSale.objects.filter(status='partially_returned').count()
    returned_pos_sales = POSSale.objects.filter(status='returned').count()
    voided_pos_sales = POSSale.objects.filter(status='voided').count()

    # Combined totals
    total_completed_sales = online_delivered_count + completed_pos_sales + partially_returned_pos_sales
    total_on_hold_pending = online_pending_count + online_confirmed_count

    # Charts data: Hourly sales today (0..23)
    hourly_sales = [0] * 24
    for sale in today_pos_qs:
        hourly_sales[sale.created_at.hour] += float(sale.total)
    for ord_obj in Order.objects.filter(created_at__range=(start_of_today, end_of_today), status='delivered'):
        hourly_sales[ord_obj.created_at.hour] += float(ord_obj.total)

    # Daily sales last 7 days (POS + Online)
    last_7_days_labels = []
    last_7_days_totals = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = timezone.make_aware(datetime.combine(day, time.min))
        day_end = timezone.make_aware(datetime.combine(day, time.max))
        day_pos_tot = POSSale.objects.filter(
            created_at__range=(day_start, day_end),
            status__in=['completed', 'partially_returned']
        ).aggregate(t=Sum('total'))['t'] or Decimal('0.00')
        day_online_tot = Order.objects.filter(
            created_at__range=(day_start, day_end),
            status='delivered'
        ).aggregate(t=Sum('total'))['t'] or Decimal('0.00')

        last_7_days_labels.append(day.strftime('%a %d %b'))
        last_7_days_totals.append(float(day_pos_tot + day_online_tot))

    # Top selling products (Combined POS + Web)
    top_products_pos = POSSaleItem.objects.filter(
        sale__status__in=['completed', 'partially_returned']
    ).values('product_name_snapshot').annotate(
        total_qty=Sum('quantity'),
        total_rev=Sum('line_total')
    ).order_by('-total_qty')[:5]

    top_products = list(top_products_pos)
    if not top_products:
        top_products_web = OrderItem.objects.filter(
            order__status='delivered'
        ).values('product_name').annotate(
            total_qty=Sum('quantity'),
            total_rev=Sum('subtotal')
        ).order_by('-total_qty')[:5]
        top_products = [{'product_name_snapshot': item['product_name'], 'total_qty': item['total_qty'], 'total_rev': item['total_rev']} for item in top_products_web]

    # Recent transactions (Combined feed)
    recent_transactions = POSSale.objects.select_related('cashier', 'customer').order_by('-created_at')[:8]

    context = {
        'settings': settings_obj,
        'today_sales_total': today_sales_total,
        'total_sales_all_time': total_sales_all_time,
        'today_transactions_count': today_transactions_count,
        'today_items_sold': today_items_sold,
        'today_avg_sale': today_avg_sale,
        'today_cash_collected': today_cash_collected,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'returns_today_count': returns_today_count,
        'hourly_sales_json': json.dumps(hourly_sales),
        'last_7_days_labels_json': json.dumps(last_7_days_labels),
        'last_7_days_totals_json': json.dumps(last_7_days_totals),
        'top_products': top_products,
        'recent_transactions': recent_transactions,
        'low_stock_products': low_stock_products[:5],

        # Sales & Order Status Metrics
        'total_online_orders': total_online_orders,
        'online_pending_count': online_pending_count,
        'online_confirmed_count': online_confirmed_count,
        'online_processing_count': online_processing_count,
        'online_delivered_count': online_delivered_count,
        'online_cancelled_count': online_cancelled_count,
        'online_revenue': online_revenue,
        'completed_pos_sales': completed_pos_sales,
        'partially_returned_pos_sales': partially_returned_pos_sales,
        'returned_pos_sales': returned_pos_sales,
        'voided_pos_sales': voided_pos_sales,
        'total_completed_sales': total_completed_sales,
        'total_on_hold_pending': total_on_hold_pending,
    }
    return render(request, 'pos/dashboard.html', context)


@pos_staff_required
def terminal(request):
    """Fullscreen POS Terminal Cashier Interface."""
    settings_obj = StoreSettings.get_settings()
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    products = Product.objects.filter(active=True).select_related('category', 'brand').order_by('name')[:60]
    customers = POSCustomer.objects.order_by('-created_at')[:20]

    context = {
        'settings': settings_obj,
        'categories': categories,
        'products': products,
        'customers': customers,
    }
    return render(request, 'pos/terminal.html', context)


@pos_staff_required
def search_products(request):
    """AJAX endpoint for searching products by name, SKU, barcode, or category."""
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category_id')
    settings_obj = StoreSettings.get_settings()
    low_thresh = settings_obj.low_stock_threshold

    products = Product.objects.filter(active=True).select_related('category', 'brand')

    if category_id:
        products = products.filter(Q(category_id=category_id) | Q(category__parent_id=category_id))

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__iexact=query) |
            Q(barcode__iexact=query) |
            Q(sku__icontains=query) |
            Q(barcode__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )

    products_list = []
    for p in products[:50]:
        stock_status = 'in_stock'
        if p.stock == 0:
            stock_status = 'out_of_stock'
        elif p.stock <= low_thresh:
            stock_status = 'low_stock'

        products_list.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku or '',
            'barcode': p.barcode or '',
            'selling_price': float(p.selling_price),
            'regular_price': float(p.regular_price),
            'discount_price': float(p.discount_price) if p.discount_price else None,
            'stock': p.stock,
            'stock_status': stock_status,
            'category_name': p.category.name if p.category else 'General',
            'image_url': p.get_main_image_url(),
        })

    return JsonResponse({'success': True, 'products': products_list})


@pos_staff_required
def search_customers(request):
    """AJAX endpoint for searching customers by name or mobile."""
    query = request.GET.get('q', '').strip()
    customers_list = []
    if query:
        customers = POSCustomer.objects.filter(
            Q(name__icontains=query) | Q(mobile__icontains=query) | Q(email__icontains=query)
        ).order_by('-created_at')[:15]
    else:
        customers = POSCustomer.objects.order_by('-created_at')[:15]

    for c in customers:
        customers_list.append({
            'id': c.id,
            'name': c.name,
            'mobile': c.mobile,
            'email': c.email or '',
        })
    return JsonResponse({'success': True, 'customers': customers_list})


@pos_staff_required
@require_POST
def add_customer(request):
    """AJAX endpoint for adding a new POS Customer."""
    name = request.POST.get('name', '').strip()
    mobile = request.POST.get('mobile', '').strip()
    email = request.POST.get('email', '').strip()
    address = request.POST.get('address', '').strip()

    if not name:
        return JsonResponse({'success': False, 'message': 'Customer name is required.'})
    if not mobile:
        return JsonResponse({'success': False, 'message': 'Mobile number is required.'})
    if not validate_bd_mobile(mobile):
        return JsonResponse({'success': False, 'message': 'Invalid Bangladesh mobile number (e.g. 01XXXXXXXXX).'})

    if POSCustomer.objects.filter(mobile=mobile).exists():
        c = POSCustomer.objects.get(mobile=mobile)
        return JsonResponse({'success': True, 'customer': {'id': c.id, 'name': c.name, 'mobile': c.mobile, 'email': c.email}, 'message': 'Existing customer loaded.'})

    customer = POSCustomer.objects.create(name=name, mobile=mobile, email=email, address=address)
    return JsonResponse({
        'success': True,
        'customer': {'id': customer.id, 'name': customer.name, 'mobile': customer.mobile, 'email': customer.email},
        'message': 'Customer added successfully.'
    })


@pos_staff_required
@require_POST
def complete_sale(request):
    """Atomic backend handler for completing a POS Cash Sale."""
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid payload.'})

    items = data.get('items', [])
    customer_id = data.get('customer_id')
    discount_type = data.get('discount_type', 'none')
    discount_val_raw = data.get('discount_value', 0)
    cash_received_raw = data.get('cash_received', 0)
    notes = data.get('notes', '')

    if not items:
        return JsonResponse({'success': False, 'message': 'POS Cart is empty.'})

    try:
        discount_val = Decimal(str(discount_val_raw))
        cash_received = Decimal(str(cash_received_raw))
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid numerical values.'})

    settings_obj = StoreSettings.get_settings()

    # Check discount permissions
    max_disc_pct = settings_obj.max_cashier_discount_percentage
    if request.user.is_superuser or 'Admin' in [g.name for g in request.user.groups.all()]:
        max_disc_pct = settings_obj.max_admin_discount_percentage

    try:
        with transaction.atomic():
            subtotal = Decimal('0.00')
            sale_items_data = []

            for item_info in items:
                product_id = item_info.get('product_id')
                qty = int(item_info.get('quantity', 1))
                if qty <= 0:
                    continue

                # Lock product row in DB
                try:
                    product = Product.objects.select_for_update().get(id=product_id, active=True)
                except Product.DoesNotExist:
                    raise ValueError(f"Product ID #{product_id} is no longer active.")

                if product.stock < qty:
                    raise ValueError(f"Insufficient stock for '{product.name}'. Only {product.stock} available.")

                unit_price = product.selling_price
                line_total = unit_price * qty
                subtotal += line_total

                sale_items_data.append({
                    'product': product,
                    'name': product.name,
                    'sku': product.sku or '',
                    'unit_price': unit_price,
                    'quantity': qty,
                    'line_total': line_total,
                })

            if not sale_items_data:
                raise ValueError("No valid products in cart.")

            # Calculate discount
            discount_amount = Decimal('0.00')
            if discount_type == 'percentage' and discount_val > 0:
                if discount_val > max_disc_pct:
                    raise ValueError(f"Discount exceeds maximum allowed permission ({max_disc_pct}%).")
                discount_amount = (subtotal * discount_val) / Decimal('100')
            elif discount_type == 'fixed' and discount_val > 0:
                discount_amount = discount_val
                eff_pct = (discount_amount / subtotal) * Decimal('100')
                if eff_pct > max_disc_pct:
                    raise ValueError(f"Fixed discount exceeds maximum allowed permission limit ({max_disc_pct}%).")

            if discount_amount > subtotal:
                discount_amount = subtotal

            total = subtotal - discount_amount

            if cash_received < total:
                raise ValueError(f"Cash received (৳{cash_received}) is less than total amount (৳{total}).")

            change_amount = cash_received - total

            # Customer lookup
            pos_customer = None
            if customer_id:
                try:
                    pos_customer = POSCustomer.objects.get(id=customer_id)
                except POSCustomer.DoesNotExist:
                    pass

            # Create POS Sale Record
            sale = POSSale.objects.create(
                cashier=request.user,
                customer=pos_customer,
                subtotal=subtotal,
                discount_type=discount_type,
                discount_value=discount_val,
                discount_amount=discount_amount,
                total=total,
                cash_received=cash_received,
                change_amount=change_amount,
                payment_method='CASH',
                payment_status='PAID',
                status='completed',
                notes=notes
            )

            # Create POS Sale Items & Deduct Inventory
            for s_item in sale_items_data:
                POSSaleItem.objects.create(
                    sale=sale,
                    product=s_item['product'],
                    product_name_snapshot=s_item['name'],
                    sku_snapshot=s_item['sku'],
                    unit_price=s_item['unit_price'],
                    quantity=s_item['quantity'],
                    line_total=s_item['line_total']
                )

                prev_stock = s_item['product'].stock
                s_item['product'].stock -= s_item['quantity']
                s_item['product'].sold_count += s_item['quantity']
                s_item['product'].save(update_fields=['stock', 'sold_count'])

                # Log inventory movement audit
                InventoryMovement.objects.create(
                    product=s_item['product'],
                    movement_type='POS_SALE',
                    quantity=-s_item['quantity'],
                    previous_stock=prev_stock,
                    new_stock=s_item['product'].stock,
                    reference_type='POSSale',
                    reference_id=sale.receipt_number,
                    staff=request.user,
                    reason=f"POS Cash Sale ({sale.receipt_number})"
                )

            return JsonResponse({
                'success': True,
                'receipt_number': sale.receipt_number,
                'redirect_url': f'/pos/receipt/{sale.receipt_number}/',
                'message': 'Sale completed successfully!'
            })

    except ValueError as ve:
        return JsonResponse({'success': False, 'message': str(ve)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An unexpected error occurred during sale completion.'})


@pos_staff_required
def receipt_detail(request, receipt_number):
    """Printable POS Receipt View."""
    sale = get_object_or_404(POSSale.objects.select_related('cashier', 'customer'), receipt_number=receipt_number)
    settings_obj = StoreSettings.get_settings()
    items = sale.items.select_related('product').all()

    context = {
        'sale': sale,
        'items': items,
        'settings': settings_obj,
    }
    return render(request, 'pos/receipt.html', context)


@pos_staff_required
def sales_history(request):
    """Filterable Sales History with 2 Categories: Offline (POS) & Online (E-Commerce Web)."""
    from orders.models import Order, OrderItem

    # Parameters & Filters
    channel_f = request.GET.get('channel', 'all').strip().lower()
    search_q = request.GET.get('q', '').strip()
    status_f = request.GET.get('status')
    cashier_id = request.GET.get('cashier_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    offline_qs = POSSale.objects.select_related('cashier', 'customer').prefetch_related('items').all()
    online_qs = Order.objects.select_related('user').prefetch_related('items').all()

    # Search Filtering
    if search_q:
        offline_qs = offline_qs.filter(
            Q(receipt_number__icontains=search_q) |
            Q(customer__name__icontains=search_q) |
            Q(customer__mobile__icontains=search_q) |
            Q(cashier__username__icontains=search_q) |
            Q(items__product_name_snapshot__icontains=search_q)
        ).distinct()

        online_qs = online_qs.filter(
            Q(order_number__icontains=search_q) |
            Q(recipient_name__icontains=search_q) |
            Q(mobile__icontains=search_q) |
            Q(district__icontains=search_q) |
            Q(items__product_name__icontains=search_q)
        ).distinct()

    # Date Filtering
    if date_from:
        try:
            d1 = datetime.strptime(date_from, '%Y-%m-%d')
            start_dt = timezone.make_aware(datetime.combine(d1, time.min))
            offline_qs = offline_qs.filter(created_at__gte=start_dt)
            online_qs = online_qs.filter(created_at__gte=start_dt)
        except ValueError:
            pass

    if date_to:
        try:
            d2 = datetime.strptime(date_to, '%Y-%m-%d')
            end_dt = timezone.make_aware(datetime.combine(d2, time.max))
            offline_qs = offline_qs.filter(created_at__lte=end_dt)
            online_qs = online_qs.filter(created_at__lte=end_dt)
        except ValueError:
            pass

    # Status Filtering
    if status_f:
        offline_qs = offline_qs.filter(status=status_f)
        online_qs = online_qs.filter(status=status_f)

    # Cashier Filtering (Applies to offline sales)
    if cashier_id:
        offline_qs = offline_qs.filter(cashier_id=cashier_id)

    sales_records = []

    # 1. Build Offline POS Sales
    if channel_f in ['all', 'offline']:
        for sale in offline_qs:
            items_list = [
                {
                    'name': item.product_name_snapshot,
                    'sku': item.sku_snapshot,
                    'qty': item.quantity,
                    'price': item.unit_price,
                    'subtotal': item.line_total,
                }
                for item in sale.items.all()
            ]
            sales_records.append({
                'channel': 'offline',
                'channel_title': 'Offline POS',
                'channel_badge_class': 'badge-channel-offline',
                'channel_icon': 'bi-calculator-fill',
                'reference_number': sale.receipt_number,
                'created_at': sale.created_at,
                'customer_name': sale.customer.name if sale.customer else 'Walk-in Customer',
                'customer_mobile': sale.customer.mobile if sale.customer else '',
                'cashier_or_source': sale.cashier.get_full_name() or sale.cashier.username,
                'items_count': sale.items.count(),
                'total_qty': sum(it['qty'] for it in items_list),
                'items_list': items_list,
                'subtotal': sale.subtotal,
                'discount_amount': sale.discount_amount,
                'total': sale.total,
                'payment_info': f"{sale.payment_method} (Cash: ৳{sale.cash_received:.0f})",
                'status': sale.status,
                'status_display': sale.get_status_display(),
                'status_badge_class': 'bg-success' if sale.status == 'completed' else ('bg-warning text-dark' if sale.status == 'partially_returned' else ('bg-danger' if sale.status == 'returned' else 'bg-secondary')),
                'detail_url': f'/pos/sale/{sale.receipt_number}/',
                'receipt_url': f'/pos/receipt/{sale.receipt_number}/',
                'can_print_receipt': True,
                'receipt_label': 'POS Receipt',
                'receipt_modal_type': 'offline',
            })

    # 2. Build Online Web Orders
    if channel_f in ['all', 'online']:
        for order in online_qs:
            items_list = [
                {
                    'name': item.product_name,
                    'sku': getattr(item.product, 'sku', '') if item.product else '',
                    'qty': item.quantity,
                    'price': item.unit_price,
                    'subtotal': item.subtotal,
                }
                for item in order.items.all()
            ]
            sales_records.append({
                'channel': 'online',
                'channel_title': 'Online Web',
                'channel_badge_class': 'badge-channel-online',
                'channel_icon': 'bi-globe-asia-australia',
                'reference_number': order.order_number,
                'created_at': order.created_at,
                'customer_name': order.recipient_name,
                'customer_mobile': order.mobile,
                'cashier_or_source': f"Online ({order.district})",
                'items_count': order.items.count(),
                'total_qty': sum(it['qty'] for it in items_list),
                'items_list': items_list,
                'subtotal': order.subtotal,
                'discount_amount': order.discount_amount,
                'total': order.total,
                'payment_info': f"{order.payment_method} • {order.get_payment_status_display()}",
                'status': order.status,
                'status_display': order.get_status_display(),
                'status_badge_class': 'bg-success' if order.status == 'delivered' else ('bg-primary' if order.status in ['confirmed', 'packed', 'handed_to_courier', 'out_for_delivery'] else ('bg-warning text-dark' if order.status == 'pending' else 'bg-secondary')),
                'detail_url': f'/pos/online-orders/?q={order.order_number}',
                'receipt_url': f'/checkout/order-confirmation/{order.order_number}/',
                'can_print_receipt': True,
                'receipt_label': 'Order Invoice',
                'receipt_modal_type': 'online',
            })

    # Sort combined sales chronologically
    sales_records.sort(key=lambda s: s['created_at'], reverse=True)

    # Aggregated Metrics
    offline_total_revenue = sum(s['total'] for s in sales_records if s['channel'] == 'offline')
    online_total_revenue = sum(s['total'] for s in sales_records if s['channel'] == 'online')
    combined_total_revenue = offline_total_revenue + online_total_revenue

    offline_sales_count = len([s for s in sales_records if s['channel'] == 'offline'])
    online_sales_count = len([s for s in sales_records if s['channel'] == 'online'])
    total_items_sold_units = sum(s['total_qty'] for s in sales_records)

    cashiers = User.objects.filter(is_staff=True)

    from django.core.paginator import Paginator
    paginator = Paginator(sales_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'cashiers': cashiers,
        'channel_filter': channel_f,
        'offline_total_revenue': offline_total_revenue,
        'online_total_revenue': online_total_revenue,
        'combined_total_revenue': combined_total_revenue,
        'offline_sales_count': offline_sales_count,
        'online_sales_count': online_sales_count,
        'total_count': len(sales_records),
        'total_items_sold_units': total_items_sold_units,
    }
    return render(request, 'pos/sales_history.html', context)


@pos_staff_required
def sale_detail(request, receipt_number):
    """View details of a single POS transaction."""
    sale = get_object_or_404(POSSale.objects.select_related('cashier', 'customer'), receipt_number=receipt_number)
    items = sale.items.select_related('product').all()
    returns = sale.returns.prefetch_related('items__product').all()
    settings_obj = StoreSettings.get_settings()

    context = {
        'sale': sale,
        'items': items,
        'returns': returns,
        'settings': settings_obj,
    }
    return render(request, 'pos/sale_detail.html', context)


@pos_staff_required
def returns_list(request):
    """Returns management and processing view."""
    returns_qs = POSReturn.objects.select_related('sale', 'staff').prefetch_related('items__product').order_by('-created_at')
    
    from django.core.paginator import Paginator
    paginator = Paginator(returns_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'total_returns_amount': returns_qs.aggregate(s=Sum('total_refund'))['s'] or Decimal('0.00'),
    }
    return render(request, 'pos/returns_list.html', context)


@pos_staff_required
@require_POST
def process_return(request):
    """Atomic backend API for partial/full returns."""
    receipt_number = request.POST.get('receipt_number', '').strip()
    reason = request.POST.get('reason', '').strip()
    items_json = request.POST.get('items_json', '[]')

    if not receipt_number or not reason:
        messages.error(request, "Receipt number and return reason are required.")
        return redirect('pos:returns_list')

    sale = get_object_or_404(POSSale, receipt_number=receipt_number)
    if sale.status == 'voided' or sale.status == 'returned':
        messages.error(request, f"Sale {receipt_number} cannot be returned (Status: {sale.get_status_display()}).")
        return redirect('pos:returns_list')

    try:
        return_items_data = json.loads(items_json)
    except Exception:
        messages.error(request, "Invalid return items format.")
        return redirect('pos:returns_list')

    if not return_items_data:
        messages.error(request, "No items selected for return.")
        return redirect('pos:returns_list')

    try:
        with transaction.atomic():
            pos_return = POSReturn.objects.create(
                sale=sale,
                staff=request.user,
                reason=reason,
                total_refund=Decimal('0.00')
            )
            total_refund = Decimal('0.00')

            for r_item in return_items_data:
                sale_item_id = r_item.get('sale_item_id')
                qty = int(r_item.get('quantity', 0))
                if qty <= 0:
                    continue

                sale_item = POSSaleItem.objects.select_for_update().get(id=sale_item_id, sale=sale)
                if qty > sale_item.remaining_returnable_quantity:
                    raise ValueError(f"Return qty ({qty}) for '{sale_item.product_name_snapshot}' exceeds remaining returnable qty ({sale_item.remaining_returnable_quantity}).")

                refund = sale_item.unit_price * qty
                total_refund += refund

                POSReturnItem.objects.create(
                    return_obj=pos_return,
                    sale_item=sale_item,
                    product=sale_item.product,
                    quantity=qty,
                    unit_price_snapshot=sale_item.unit_price,
                    refund_amount=refund
                )

                sale_item.returned_quantity += qty
                sale_item.save(update_fields=['returned_quantity'])

                # Restore inventory
                if sale_item.product:
                    prod = Product.objects.select_for_update().get(id=sale_item.product.id)
                    prev_stock = prod.stock
                    prod.stock += qty
                    prod.save(update_fields=['stock'])

                    InventoryMovement.objects.create(
                        product=prod,
                        movement_type='POS_RETURN',
                        quantity=qty,
                        previous_stock=prev_stock,
                        new_stock=prod.stock,
                        reference_type='POSReturn',
                        reference_id=pos_return.return_number,
                        staff=request.user,
                        reason=f"POS Return restock ({pos_return.return_number})"
                    )

            pos_return.total_refund = total_refund
            pos_return.save(update_fields=['total_refund'])

            # Update sale status
            all_returned = all(si.remaining_returnable_quantity == 0 for si in sale.items.all())
            sale.status = 'returned' if all_returned else 'partially_returned'
            sale.save(update_fields=['status'])

            messages.success(request, f"Return {pos_return.return_number} processed successfully! Refund amount: ৳{total_refund}")
            return redirect('pos:sale_detail', receipt_number=sale.receipt_number)

    except Exception as e:
        messages.error(request, f"Return processing failed: {str(e)}")
        return redirect('pos:returns_list')


@pos_staff_required
@require_POST
def void_sale(request, receipt_number):
    """Void a sale and restore inventory with staff permission check."""
    if not (request.user.is_superuser or request.user.has_perm('pos.delete_possale')):
        messages.error(request, "Permission denied. Only Super Admin can void sales.")
        return redirect('pos:sale_detail', receipt_number=receipt_number)

    sale = get_object_or_404(POSSale, receipt_number=receipt_number)
    if sale.status == 'voided':
        messages.info(request, "Sale is already voided.")
        return redirect('pos:sale_detail', receipt_number=receipt_number)

    reason = request.POST.get('reason', 'Voided by Administrator')

    with transaction.atomic():
        sale.status = 'voided'
        sale.notes = f"{sale.notes}\n[VOIDED]: {reason}"
        sale.save(update_fields=['status', 'notes'])

        # Restore inventory for unreturned quantities
        for item in sale.items.all():
            qty_to_restore = item.remaining_returnable_quantity
            if qty_to_restore > 0 and item.product:
                prod = Product.objects.select_for_update().get(id=item.product.id)
                prev_stock = prod.stock
                prod.stock += qty_to_restore
                prod.save(update_fields=['stock'])

                InventoryMovement.objects.create(
                    product=prod,
                    movement_type='POS_RETURN',
                    quantity=qty_to_restore,
                    previous_stock=prev_stock,
                    new_stock=prod.stock,
                    reference_type='POSSaleVoid',
                    reference_id=sale.receipt_number,
                    staff=request.user,
                    reason=f"Sale Void stock restoration ({sale.receipt_number})"
                )

    messages.success(request, f"Sale {receipt_number} has been voided and inventory restored.")
    return redirect('pos:sale_detail', receipt_number=receipt_number)


@pos_staff_required
def reports(request):
    """Comprehensive Dynamic Reports & Analytics."""
    period = request.GET.get('period', 'today')
    today = timezone.now().date()

    if period == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif period == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == 'month':
        start_date = today.replace(day=1)
        end_date = today
    elif period == 'custom':
        try:
            start_date = datetime.strptime(request.GET.get('date_from'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('date_to'), '%Y-%m-%d').date()
        except Exception:
            start_date = today
            end_date = today
    else:
        start_date = today
        end_date = today

    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

    sales_qs = POSSale.objects.filter(created_at__range=(start_datetime, end_datetime), status__in=['completed', 'partially_returned'])
    returns_qs = POSReturn.objects.filter(created_at__range=(start_datetime, end_datetime))

    gross_sales = sales_qs.aggregate(s=Sum('subtotal'))['s'] or Decimal('0.00')
    discounts_total = sales_qs.aggregate(s=Sum('discount_amount'))['s'] or Decimal('0.00')
    returns_total = returns_qs.aggregate(s=Sum('total_refund'))['s'] or Decimal('0.00')
    net_sales = sales_qs.aggregate(s=Sum('total'))['s'] or Decimal('0.00') - returns_total
    transactions_count = sales_qs.count()

    items_sold = POSSaleItem.objects.filter(sale__in=sales_qs).aggregate(s=Sum('quantity'))['s'] or 0
    avg_sale_val = (net_sales / transactions_count) if transactions_count > 0 else Decimal('0.00')

    # Cashier performance
    cashier_perf = sales_qs.values('cashier__username', 'cashier__first_name', 'cashier__last_name').annotate(
        trans_count=Count('id'),
        revenue=Sum('total'),
        avg_trans=Avg('total')
    ).order_by('-revenue')

    # Category performance
    cat_perf = POSSaleItem.objects.filter(sale__in=sales_qs).values(
        'product__category__name'
    ).annotate(
        units_sold=Sum('quantity'),
        revenue=Sum('line_total')
    ).order_by('-revenue')

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'gross_sales': gross_sales,
        'discounts_total': discounts_total,
        'returns_total': returns_total,
        'net_sales': net_sales,
        'transactions_count': transactions_count,
        'items_sold': items_sold,
        'avg_sale_val': avg_sale_val,
        'cashier_perf': cashier_perf,
        'cat_perf': cat_perf,
    }
    return render(request, 'pos/reports.html', context)


@pos_staff_required
def inventory(request):
    """Inventory Management & Audit Log Ledger."""
    settings_obj = StoreSettings.get_settings()
    low_thresh = settings_obj.low_stock_threshold

    products_qs = Product.objects.select_related('category', 'brand').order_by('stock', 'name')
    movements_qs = InventoryMovement.objects.select_related('product', 'staff').order_by('-created_at')[:40]

    from django.core.paginator import Paginator
    paginator = Paginator(products_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'movements': movements_qs,
        'low_threshold': low_thresh,
    }
    return render(request, 'pos/inventory.html', context)


@pos_staff_required
@require_POST
def adjust_stock(request):
    """Manual inventory stock adjustment with audit movement log."""
    product_id = request.POST.get('product_id')
    new_stock = int(request.POST.get('new_stock', 0))
    reason = request.POST.get('reason', 'Manual Admin Stock Adjustment').strip()

    product = get_object_or_404(Product, id=product_id)
    with transaction.atomic():
        prev_stock = product.stock
        diff = new_stock - prev_stock
        product.stock = new_stock
        product.save(update_fields=['stock'])

        InventoryMovement.objects.create(
            product=product,
            movement_type='MANUAL_ADJUSTMENT',
            quantity=diff,
            previous_stock=prev_stock,
            new_stock=new_stock,
            reference_type='ManualAdjustment',
            staff=request.user,
            reason=reason
        )

    messages.success(request, f"Stock for '{product.name}' updated from {prev_stock} to {new_stock}.")
    return redirect('pos:inventory')


@pos_staff_required
def settings_view(request):
    """Dynamic Store Settings Configuration."""
    settings_obj = StoreSettings.get_settings()
    if request.method == 'POST':
        settings_obj.store_name = request.POST.get('store_name', settings_obj.store_name)
        settings_obj.phone = request.POST.get('phone', settings_obj.phone)
        settings_obj.email = request.POST.get('email', settings_obj.email)
        settings_obj.address = request.POST.get('address', settings_obj.address)
        settings_obj.receipt_prefix = request.POST.get('receipt_prefix', settings_obj.receipt_prefix)
        settings_obj.receipt_footer = request.POST.get('receipt_footer', settings_obj.receipt_footer)
        settings_obj.low_stock_threshold = int(request.POST.get('low_stock_threshold', settings_obj.low_stock_threshold))
        settings_obj.allow_pos_discount = bool(request.POST.get('allow_pos_discount'))
        settings_obj.max_cashier_discount_percentage = Decimal(request.POST.get('max_cashier_discount_percentage', '10.00'))
        
        if request.FILES.get('store_logo'):
            settings_obj.store_logo = request.FILES['store_logo']

        settings_obj.save()
        messages.success(request, "Store settings updated successfully.")
        return redirect('pos:settings')

    return render(request, 'pos/settings.html', {'settings': settings_obj})


@pos_staff_required
def online_orders(request):
    """Online E-Commerce Website Orders Management Panel."""
    from orders.models import Order, ORDER_STATUS_CHOICES, PAYMENT_STATUS_CHOICES, COURIER_CHOICES

    orders_qs = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')

    # Filters
    search_q = request.GET.get('q', '').strip()
    status_f = request.GET.get('status')
    payment_status_f = request.GET.get('payment_status')

    if search_q:
        orders_qs = orders_qs.filter(
            Q(order_number__icontains=search_q) |
            Q(recipient_name__icontains=search_q) |
            Q(mobile__icontains=search_q) |
            Q(district__icontains=search_q)
        )
    if status_f:
        orders_qs = orders_qs.filter(status=status_f)
    if payment_status_f:
        orders_qs = orders_qs.filter(payment_status=payment_status_f)

    from django.core.paginator import Paginator
    paginator = Paginator(orders_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'order_statuses': ORDER_STATUS_CHOICES,
        'payment_statuses': PAYMENT_STATUS_CHOICES,
        'couriers': COURIER_CHOICES,
        'total_count': orders_qs.count(),
    }
    return render(request, 'pos/online_orders.html', context)


@pos_staff_required
@require_POST
def update_order_status(request, order_number):
    """Update online order status, payment status, courier & tracking info."""
    from orders.models import Order
    order = get_object_or_404(Order, order_number=order_number)

    new_status = request.POST.get('status', order.status)
    new_payment_status = request.POST.get('payment_status', order.payment_status)
    courier = request.POST.get('courier', order.courier)
    tracking_code = request.POST.get('tracking_code', order.tracking_code).strip()
    notes = request.POST.get('notes', '').strip()

    prev_status = order.status

    with transaction.atomic():
        order.status = new_status
        order.payment_status = new_payment_status
        order.courier = courier
        order.tracking_code = tracking_code
        if notes:
            order.notes = f"{order.notes}\n[{timezone.now().strftime('%d %b %g:%i %A')} - {request.user.username}]: {notes}"

        # If delivered, auto mark payment as paid if pending
        if new_status == 'delivered' and order.payment_status == 'pending':
            order.payment_status = 'paid'

        # If cancelled from non-cancelled state, restore inventory
        if new_status == 'cancelled' and prev_status != 'cancelled':
            for item in order.items.all():
                if item.product:
                    prod = Product.objects.select_for_update().get(id=item.product.id)
                    prev_stock = prod.stock
                    prod.stock += item.quantity
                    prod.sold_count = max(0, prod.sold_count - item.quantity)
                    prod.save(update_fields=['stock', 'sold_count'])

                    InventoryMovement.objects.create(
                        product=prod,
                        movement_type='ORDER_CANCEL',
                        quantity=item.quantity,
                        previous_stock=prev_stock,
                        new_stock=prod.stock,
                        reference_type='OrderCancel',
                        reference_id=order.order_number,
                        staff=request.user,
                        reason=f"Online order cancelled by staff ({order.order_number})"
                    )

        order.save()

    messages.success(request, f"Order {order.order_number} updated to '{order.get_status_display()}' successfully!")
    return redirect('pos:online_orders')


@pos_staff_required
def pos_products(request):
    """POS Product Catalog Management & Upload View."""
    search_q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category_id')

    products_qs = Product.objects.select_related('category', 'brand').order_by('-created_at')

    if search_q:
        products_qs = products_qs.filter(
            Q(name__icontains=search_q) |
            Q(sku__icontains=search_q) |
            Q(barcode__icontains=search_q) |
            Q(brand__name__icontains=search_q)
        )
    if category_id:
        products_qs = products_qs.filter(category_id=category_id)

    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')

    from django.core.paginator import Paginator
    paginator = Paginator(products_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'total_count': products_qs.count(),
    }
    return render(request, 'pos/products.html', context)


@pos_staff_required
def add_product(request):
    """Upload/Create a new Product from POS Panel."""
    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        regular_price = Decimal(request.POST.get('regular_price', '0'))
        discount_price_raw = request.POST.get('discount_price', '').strip()
        discount_price = Decimal(discount_price_raw) if discount_price_raw else None
        stock = int(request.POST.get('stock', 0))
        short_description = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()
        barcode = request.POST.get('barcode', '').strip()
        active = bool(request.POST.get('active'))
        featured = bool(request.POST.get('featured'))
        flash_sale = bool(request.POST.get('flash_sale'))
        trending = bool(request.POST.get('trending'))

        if not name or not category_id or regular_price <= 0:
            messages.error(request, "Product name, category, and valid regular price are required.")
            return render(request, 'pos/product_form.html', {'categories': categories, 'brands': brands})

        category = get_object_or_404(Category, id=category_id)
        brand = Brand.objects.filter(id=brand_id).first() if brand_id else None

        with transaction.atomic():
            product = Product.objects.create(
                name=name,
                category=category,
                brand=brand,
                regular_price=regular_price,
                discount_price=discount_price,
                stock=stock,
                short_description=short_description,
                description=description,
                barcode=barcode or None,
                active=active,
                featured=featured,
                flash_sale=flash_sale,
                trending=trending,
                image=request.FILES.get('image')
            )

            # Log initial restock inventory movement
            if stock > 0:
                InventoryMovement.objects.create(
                    product=product,
                    movement_type='RESTOCK',
                    quantity=stock,
                    previous_stock=0,
                    new_stock=stock,
                    reference_type='ProductCreation',
                    reference_id=str(product.id),
                    staff=request.user,
                    reason=f"Initial Product Upload Stock ({product.sku})"
                )

        messages.success(request, f"Product '{product.name}' uploaded successfully! SKU: {product.sku}, Barcode: {product.barcode}")
        return redirect('pos:pos_products')

    return render(request, 'pos/product_form.html', {'categories': categories, 'brands': brands})


@pos_staff_required
def edit_product(request, product_id):
    """Edit existing Product details from POS Panel."""
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        product.name = request.POST.get('name', product.name).strip()
        cat_id = request.POST.get('category')
        if cat_id:
            product.category = get_object_or_404(Category, id=cat_id)
        b_id = request.POST.get('brand')
        product.brand = Brand.objects.filter(id=b_id).first() if b_id else None

        product.regular_price = Decimal(request.POST.get('regular_price', str(product.regular_price)))
        dp_raw = request.POST.get('discount_price', '').strip()
        product.discount_price = Decimal(dp_raw) if dp_raw else None
        
        new_stock = int(request.POST.get('stock', product.stock))
        if new_stock != product.stock:
            diff = new_stock - product.stock
            prev_stock = product.stock
            product.stock = new_stock
            InventoryMovement.objects.create(
                product=product,
                movement_type='MANUAL_ADJUSTMENT',
                quantity=diff,
                previous_stock=prev_stock,
                new_stock=new_stock,
                reference_type='ProductEdit',
                reference_id=str(product.id),
                staff=request.user,
                reason="Stock count updated during Product Edit"
            )

        product.short_description = request.POST.get('short_description', product.short_description).strip()
        product.description = request.POST.get('description', product.description).strip()
        barcode_input = request.POST.get('barcode', '').strip()
        if barcode_input:
            product.barcode = barcode_input

        product.active = bool(request.POST.get('active'))
        product.featured = bool(request.POST.get('featured'))
        product.flash_sale = bool(request.POST.get('flash_sale'))
        product.trending = bool(request.POST.get('trending'))

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        messages.success(request, f"Product '{product.name}' updated successfully.")
        return redirect('pos:pos_products')

    return render(request, 'pos/product_form.html', {
        'product': product,
        'categories': categories,
        'brands': brands,
        'is_edit': True
    })
