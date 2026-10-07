from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from datetime import timedelta
import csv

from store.models import Product, ProductImage, FAQ, StoreSettings, IPhoneModel
from orders.models import Order, OrderItem
from .models import PageVisit
from .forms import ProductForm, ProductImageForm, FAQForm, StoreSettingsForm, OrderStatusUpdateForm


@staff_member_required
def dashboard_home(request):
    """
    Main store dashboard with live KPIs, sales, orders, cash flow, and visitor metrics.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # 1. Orders & Sales KPIs
    all_orders = Order.objects.all()
    total_orders_count = all_orders.count()
    pending_orders_count = all_orders.filter(order_status='pending').count()
    orders_today_count = all_orders.filter(created_at__gte=today_start).count()
    
    # Financials (Delivered or Confirmed sales)
    gross_sales = all_orders.exclude(order_status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0
    sales_this_month = all_orders.exclude(order_status='cancelled').filter(created_at__gte=month_start).aggregate(total=Sum('total_amount'))['total'] or 0
    sales_today = all_orders.exclude(order_status='cancelled').filter(created_at__gte=today_start).aggregate(total=Sum('total_amount'))['total'] or 0

    # 2. Cash Flow by Payment Status & Method
    paid_total = all_orders.filter(payment_status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    pending_verification_total = all_orders.filter(payment_status='pending_verification').aggregate(total=Sum('total_amount'))['total'] or 0
    unpaid_total = all_orders.filter(payment_status='unpaid').aggregate(total=Sum('total_amount'))['total'] or 0

    cash_flow_methods = {
        'cod': all_orders.filter(payment_method='cod').exclude(order_status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0,
        'bkash': all_orders.filter(payment_method='bkash').exclude(order_status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0,
        'nagad': all_orders.filter(payment_method='nagad').exclude(order_status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0,
        'rocket': all_orders.filter(payment_method='rocket').exclude(order_status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0,
        'bank': all_orders.filter(payment_method='bank_transfer').exclude(order_status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0,
    }

    # 3. Visitor & Traffic Analytics
    total_page_views = PageVisit.objects.count()
    visits_today = PageVisit.objects.filter(timestamp__gte=today_start).count()
    unique_visitors_today = PageVisit.objects.filter(timestamp__gte=today_start).values('session_key').distinct().count()
    unique_visitors_week = PageVisit.objects.filter(timestamp__gte=week_ago).values('session_key').distinct().count()
    unique_visitors_month = PageVisit.objects.filter(timestamp__gte=month_start).values('session_key').distinct().count()

    # 4. Inventory Health
    all_products = Product.objects.all()
    total_listings = all_products.count()
    available_stock = all_products.filter(status='available').count()
    reserved_stock = all_products.filter(status='reserved').count()
    sold_stock = all_products.filter(status='sold').count()
    inventory_value = all_products.filter(status='available').aggregate(total=Sum('price'))['total'] or 0

    # 5. Recent Orders
    recent_orders = all_orders.prefetch_related('items').order_by('-created_at')[:8]

    # 6. Top Visited Pages
    top_pages = PageVisit.objects.values('path').annotate(hits=Count('id')).order_by('-hits')[:5]

    # 7. Daily sales chart data for the last 7 days
    daily_labels = []
    daily_sales = []
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_total = all_orders.exclude(order_status='cancelled').filter(
            created_at__date=day_date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        daily_labels.append(day_date.strftime('%a (%d %b)'))
        daily_sales.append(int(day_total))

    context = {
        'gross_sales': gross_sales,
        'sales_this_month': sales_this_month,
        'sales_today': sales_today,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'orders_today_count': orders_today_count,
        
        'paid_total': paid_total,
        'pending_verification_total': pending_verification_total,
        'unpaid_total': unpaid_total,
        'cash_flow_methods': cash_flow_methods,

        'total_page_views': total_page_views,
        'visits_today': visits_today,
        'unique_visitors_today': unique_visitors_today,
        'unique_visitors_week': unique_visitors_week,
        'unique_visitors_month': unique_visitors_month,

        'total_listings': total_listings,
        'available_stock': available_stock,
        'reserved_stock': reserved_stock,
        'sold_stock': sold_stock,
        'inventory_value': inventory_value,

        'recent_orders': recent_orders,
        'top_pages': top_pages,
        'daily_labels': daily_labels,
        'daily_sales': daily_sales,
    }
    return render(request, 'dashboard/index.html', context)


@staff_member_required
def analytics_view(request):
    """
    Detailed analytics report: Visitor traffic, cash flow, payment distribution, popular models.
    """
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 30-day traffic breakdown
    traffic_labels = []
    traffic_views = []
    traffic_uniques = []
    for i in range(29, -1, -1):
        target_date = (now - timedelta(days=i)).date()
        day_visits = PageVisit.objects.filter(timestamp__date=target_date)
        views_count = day_visits.count()
        uniques_count = day_visits.values('session_key').distinct().count()
        
        traffic_labels.append(target_date.strftime('%d %b'))
        traffic_views.append(views_count)
        traffic_uniques.append(uniques_count)

    # Cash flow breakdown by payment method
    orders = Order.objects.exclude(order_status='cancelled')
    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 1

    payment_breakdown = []
    for method, label in Order.PAYMENT_METHOD_CHOICES:
        code = method
        m_orders = orders.filter(payment_method=code)
        m_total = m_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        m_count = m_orders.count()
        pct = (m_total / total_sales) * 100 if total_sales > 0 else 0
        payment_breakdown.append({
            'code': code,
            'label': label.split('/')[0].strip(),
            'total': m_total,
            'count': m_count,
            'percentage': round(pct, 1)
        })

    # Top iPhone models ordered
    ordered_items = OrderItem.objects.values('product_model').annotate(
        total_units=Sum('quantity'),
        revenue=Sum('price')
    ).order_by('-total_units')

    # Top Referrers
    referrers = PageVisit.objects.exclude(referer='').values('referer').annotate(
        count=Count('id')
    ).order_by('-count')[:8]

    context = {
        'traffic_labels': traffic_labels,
        'traffic_views': traffic_views,
        'traffic_uniques': traffic_uniques,
        'payment_breakdown': payment_breakdown,
        'ordered_items': ordered_items,
        'referrers': referrers,
        'total_sales': total_sales,
    }
    return render(request, 'dashboard/analytics.html', context)


@staff_member_required
def order_list(request):
    """
    Manage all incoming customer orders with filters and search.
    """
    queryset = Order.objects.prefetch_related('items').order_by('-created_at')

    # Filters
    order_status = request.GET.get('order_status')
    payment_status = request.GET.get('payment_status')
    payment_method = request.GET.get('payment_method')
    query = request.GET.get('q', '').strip()

    if order_status:
        queryset = queryset.filter(order_status=order_status)
    if payment_status:
        queryset = queryset.filter(payment_status=payment_status)
    if payment_method:
        queryset = queryset.filter(payment_method=payment_method)
    if query:
        queryset = queryset.filter(
            Q(order_number__icontains=query) |
            Q(full_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(payment_trx_id__icontains=query) |
            Q(delivery_address__icontains=query)
        )

    # Counts
    counts = {
        'all': Order.objects.count(),
        'pending': Order.objects.filter(order_status='pending').count(),
        'confirmed': Order.objects.filter(order_status='confirmed').count(),
        'shipped': Order.objects.filter(order_status='shipped').count(),
        'delivered': Order.objects.filter(order_status='delivered').count(),
        'pending_verification': Order.objects.filter(payment_status='pending_verification').count(),
    }

    context = {
        'orders': queryset,
        'counts': counts,
        'selected_order_status': order_status,
        'selected_payment_status': payment_status,
        'selected_payment_method': payment_method,
        'search_query': query,
    }
    return render(request, 'dashboard/orders/list.html', context)


@staff_member_required
def order_detail(request, order_id):
    """
    View complete order details, customer notes, TrxID verification, and update status.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id)
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.order_number} status updated successfully.")
            return redirect('dashboard:order_detail', order_id=order.id)
    else:
        form = OrderStatusUpdateForm(instance=order)

    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'dashboard/orders/detail.html', context)


@staff_member_required
def order_export_csv(request):
    """
    Export orders list to CSV spreadsheet.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="gadget_deluxe_orders_{timezone.now():%Y%m%d}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Order Number', 'Date', 'Customer Name', 'Phone', 'Email', 
        'Delivery Address', 'City', 'Payment Method', 'Sender Number', 'TrxID', 
        'Payment Status', 'Order Status', 'Subtotal (BDT)', 'Delivery (BDT)', 'Total (BDT)', 'Products'
    ])

    orders = Order.objects.prefetch_related('items').order_by('-created_at')
    for o in orders:
        items_str = "; ".join([f"{item.product_title} ({item.product_sku})" for item in o.items.all()])
        writer.writerow([
            o.order_number,
            o.created_at.strftime('%Y-%m-%d %H:%M'),
            o.full_name,
            o.phone,
            o.email or '',
            o.delivery_address,
            o.get_city_display(),
            o.get_payment_method_display(),
            o.payment_sender_number or '',
            o.payment_trx_id or '',
            o.get_payment_status_display(),
            o.get_order_status_display(),
            o.subtotal,
            o.delivery_charge,
            o.total_amount,
            items_str
        ])

    return response


@staff_member_required
def product_list(request):
    """
    Product inventory manager with search and quick actions.
    """
    queryset = Product.objects.select_related('model').prefetch_related('images').order_by('-created_at')

    model_slug = request.GET.get('model')
    status = request.GET.get('status')
    query = request.GET.get('q', '').strip()

    if model_slug:
        queryset = queryset.filter(model__slug=model_slug)
    if status:
        queryset = queryset.filter(status=status)
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(sku__icontains=query) |
            Q(color__icontains=query)
        )

    models_list = IPhoneModel.objects.filter(is_active=True).order_by('order')

    context = {
        'products': queryset,
        'models_list': models_list,
        'selected_model': model_slug,
        'selected_status': status,
        'search_query': query,
    }
    return render(request, 'dashboard/products/list.html', context)


@staff_member_required
def product_create(request):
    """
    Create a new used iPhone listing.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"New listing '{product.title}' created successfully with SKU {product.sku}.")
            return redirect('dashboard:product_edit', product_id=product.id)
    else:
        form = ProductForm()

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'dashboard/products/form.html', context)


@staff_member_required
def product_edit(request, product_id):
    """
    Edit iPhone listing parameters, specifications, price, and gallery photos.
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            
            # Handle additional gallery images upload
            gallery_files = request.FILES.getlist('extra_images')
            for f in gallery_files:
                ProductImage.objects.create(product=product, image=f)

            messages.success(request, f"Listing '{product.title}' updated successfully.")
            return redirect('dashboard:product_edit', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'is_edit': True,
    }
    return render(request, 'dashboard/products/form.html', context)


@staff_member_required
def product_delete(request, product_id):
    """
    Delete an iPhone listing.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f"Listing '{title}' deleted successfully.")
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/products/delete_confirm.html', {'product': product})


@staff_member_required
def product_toggle_status(request, product_id, new_status):
    """
    Quickly toggle status between 'available', 'reserved', and 'sold'.
    """
    product = get_object_or_404(Product, id=product_id)
    if new_status in ['available', 'reserved', 'sold']:
        product.status = new_status
        product.save(update_fields=['status'])
        messages.success(request, f"Status for {product.sku} updated to {product.get_status_display()}.")
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:product_list')


@staff_member_required
def product_image_delete(request, image_id):
    """
    Delete an extra gallery photo.
    """
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    image.delete()
    messages.info(request, "Gallery photo removed.")
    return redirect('dashboard:product_edit', product_id=product_id)


@staff_member_required
def faq_list(request):
    """
    Manage FAQs in English & Bangla.
    """
    faqs = FAQ.objects.all().order_by('category', 'order')
    return render(request, 'dashboard/faqs/list.html', {'faqs': faqs})


@staff_member_required
def faq_create(request):
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save()
            messages.success(request, f"FAQ item added successfully.")
            return redirect('dashboard:faq_list')
    else:
        form = FAQForm()
    return render(request, 'dashboard/faqs/form.html', {'form': form, 'is_edit': False})


@staff_member_required
def faq_edit(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ item updated successfully.")
            return redirect('dashboard:faq_list')
    else:
        form = FAQForm(instance=faq)
    return render(request, 'dashboard/faqs/form.html', {'form': form, 'faq': faq, 'is_edit': True})


@staff_member_required
def faq_delete(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        faq.delete()
        messages.success(request, "FAQ item deleted.")
        return redirect('dashboard:faq_list')
    return render(request, 'dashboard/faqs/delete_confirm.html', {'faq': faq})


@staff_member_required
def store_settings_view(request):
    """
    Manage store hotline, WhatsApp, bKash, Nagad, Rocket, Bank account details, and delivery charges.
    """
    settings_obj = StoreSettings.get_settings()
    if request.method == 'POST':
        form = StoreSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Store & Payment Settings saved successfully.")
            return redirect('dashboard:settings')
    else:
        form = StoreSettingsForm(instance=settings_obj)

    return render(request, 'dashboard/settings.html', {'form': form, 'settings': settings_obj})
