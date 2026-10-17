from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from datetime import timedelta
import csv
import secrets
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from store.models import Product, ProductImage, FAQ, StoreSettings, IPhoneModel, Review
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

            # Handle additional gallery images upload
            gallery_files = request.FILES.getlist('extra_images')
            from store.image_utils import process_image_file
            for f in gallery_files:
                converted_f = process_image_file(f)
                ProductImage.objects.create(product=product, image=converted_f)

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
            from store.image_utils import process_image_file
            for f in gallery_files:
                converted_f = process_image_file(f)
                ProductImage.objects.create(product=product, image=converted_f)

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

    password_form = PasswordChangeForm(user=request.user)

    return render(request, 'dashboard/settings.html', {
        'form': form,
        'settings': settings_obj,
        'password_form': password_form,
    })


@staff_member_required
def send_admin_otp_view(request):
    """
    Generate and dispatch a 6-digit OTP code to the administrator's email
    for verifying username, email, or password modifications.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method is allowed.'}, status=405)

    target_email = request.POST.get('email', '').strip() or request.user.email
    if not target_email or '@' not in target_email:
        return JsonResponse({'success': False, 'message': 'Please provide a valid email address.'}, status=400)

    # Generate 6-digit cryptographic OTP code
    otp_code = f"{secrets.randbelow(900000) + 100000}"

    # Save to admin session with 10-minute expiry
    request.session['admin_otp'] = {
        'code': otp_code,
        'email': target_email,
        'expires_at': (timezone.now() + timedelta(minutes=10)).isoformat(),
        'created_at': timezone.now().isoformat(),
    }
    request.session.modified = True

    # Compose and dispatch email
    subject = f"[Gadget Deluxe] Admin Security OTP: {otp_code}"
    body_text = (
        f"Hello {request.user.username},\n\n"
        f"Your verification code to modify your Gadget Deluxe administrator credentials "
        f"(username, email, or password) is:\n\n"
        f"    {otp_code}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"If you did not initiate this request, please review your store account security immediately.\n\n"
        f"— Gadget Deluxe Security Team\n"
        f"https://www.gadgetdeluxe.shop"
    )

    sent_successfully = False
    try:
        send_mail(
            subject=subject,
            message=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            fail_silently=False,
        )
        sent_successfully = True
    except Exception as e:
        # In development or if SMTP is offline, log OTP to console
        print(f"[SECURITY OTP] Failed to send email via SMTP: {e}. Active OTP for {target_email} is: {otp_code}")

    msg = f"A 6-digit verification code has been dispatched to {target_email}."
    return JsonResponse({
        'success': True,
        'message': msg,
        'email': target_email,
        'dev_otp': otp_code if (settings.DEBUG or not sent_successfully) else None,
    })


@staff_member_required
def change_password_view(request):
    """
    Allow staff members and store administrators to change their username, email,
    and password directly from the shop admin panel with Email OTP verification.
    """
    user = request.user
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        otp_entered = request.POST.get('otp', '').strip()

        errors = []

        # 1. Validate Current Password
        if not user.check_password(current_password):
            errors.append("Current admin password is incorrect.")

        # 2. Validate OTP
        otp_session = request.session.get('admin_otp')
        if not otp_session:
            errors.append("No verification code found. Please click 'Send OTP' to your email first.")
        else:
            try:
                expires_at = timezone.datetime.fromisoformat(otp_session['expires_at'])
                if timezone.now() > expires_at:
                    errors.append("Verification code has expired. Please request a new OTP.")
                elif otp_session['code'] != otp_entered:
                    errors.append("Invalid verification code (OTP). Please check your email and try again.")
            except Exception:
                errors.append("Invalid OTP session. Please request a new OTP.")

        # 3. Validate Username
        if not new_username:
            errors.append("Username cannot be empty.")
        elif new_username != user.username and User.objects.filter(username__iexact=new_username).exclude(id=user.id).exists():
            errors.append(f"Username '{new_username}' is already taken by another account.")

        # 4. Validate Email
        if not new_email or '@' not in new_email:
            errors.append("Please enter a valid email address.")

        # 5. Validate Password (if provided)
        if new_password or confirm_password:
            if len(new_password) < 8:
                errors.append("New password must be at least 8 characters long.")
            if new_password != confirm_password:
                errors.append("New password and confirmation password do not match.")

        if errors:
            for err in errors:
                messages.error(request, err)
        else:
            # Apply Changes
            user.username = new_username
            user.email = new_email
            if new_password:
                user.set_password(new_password)
            user.save()

            # Clear used OTP
            request.session.pop('admin_otp', None)
            request.session.modified = True

            # Keep user authenticated
            update_session_auth_hash(request, user)
            messages.success(request, "Administrator credentials successfully verified and updated!")
            return redirect('dashboard:change_password')

    return render(request, 'dashboard/change_password.html', {
        'admin_user': user,
    })


# ==============================================================================
# CUSTOMER MANAGEMENT VIEWS
# ==============================================================================

@staff_member_required
def customer_list(request):
    """
    Consolidated Customer Management View.
    Aggregates both registered users and guest checkout customers.
    """
    search_query = request.GET.get('q', '').strip()
    customer_type = request.GET.get('type', '')  # 'registered', 'guest', ''
    
    # 1. Fetch all orders and reviews
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
    reviews = Review.objects.select_related('user', 'product').order_by('-created_at')
    registered_users = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    # We will build a unified dictionary keyed by customer identity
    customers_map = {}
    
    # Add registered users first
    for u in registered_users:
        key = f"u-{u.id}"
        customers_map[key] = {
            'key': key,
            'user': u,
            'name': u.get_full_name() or u.username,
            'phone': '',
            'email': u.email,
            'is_registered': True,
            'orders': [],
            'reviews': [],
            'total_spent': 0,
            'orders_count': 0,
            'reviews_count': 0,
            'last_active': u.date_joined,
            'address': '',
            'city': '',
        }
    
    # Add orders to customers
    for order in orders:
        if order.user:
            key = f"u-{order.user.id}"
            if key not in customers_map:
                customers_map[key] = {
                    'key': key,
                    'user': order.user,
                    'name': order.full_name or order.user.get_full_name() or order.user.username,
                    'phone': order.phone,
                    'email': order.email or order.user.email,
                    'is_registered': True,
                    'orders': [],
                    'reviews': [],
                    'total_spent': 0,
                    'orders_count': 0,
                    'reviews_count': 0,
                    'last_active': order.created_at,
                    'address': order.delivery_address,
                    'city': order.get_city_display(),
                }
            c = customers_map[key]
            c['orders'].append(order)
            if not c['phone'] and order.phone:
                c['phone'] = order.phone
            if not c['email'] and order.email:
                c['email'] = order.email
            if order.order_status != 'cancelled':
                c['total_spent'] += order.total_amount
            if not c['address'] and order.delivery_address:
                c['address'] = order.delivery_address
                c['city'] = order.get_city_display()
            if order.created_at > c['last_active']:
                c['last_active'] = order.created_at
        else:
            # Guest order, key by phone (or order id fallback)
            clean_phone = order.phone.strip() if order.phone else ''
            key = f"p-{clean_phone}" if clean_phone else f"o-{order.id}"
            if key not in customers_map:
                customers_map[key] = {
                    'key': key,
                    'user': None,
                    'name': order.full_name,
                    'phone': order.phone,
                    'email': order.email or '',
                    'is_registered': False,
                    'orders': [],
                    'reviews': [],
                    'total_spent': 0,
                    'orders_count': 0,
                    'reviews_count': 0,
                    'last_active': order.created_at,
                    'address': order.delivery_address,
                    'city': order.get_city_display(),
                }
            c = customers_map[key]
            c['orders'].append(order)
            if order.order_status != 'cancelled':
                c['total_spent'] += order.total_amount
            if order.created_at > c['last_active']:
                c['last_active'] = order.created_at
            if not c['address'] and order.delivery_address:
                c['address'] = order.delivery_address
                c['city'] = order.get_city_display()

    # Link reviews to customers
    for rev in reviews:
        if rev.user:
            key = f"u-{rev.user.id}"
            if key in customers_map:
                customers_map[key]['reviews'].append(rev)
        elif rev.customer_phone:
            clean_phone = rev.customer_phone.strip()
            key = f"p-{clean_phone}"
            if key in customers_map:
                customers_map[key]['reviews'].append(rev)
            else:
                # Customer who left a review but no recorded orders yet
                customers_map[key] = {
                    'key': key,
                    'user': None,
                    'name': rev.customer_name,
                    'phone': rev.customer_phone,
                    'email': rev.customer_email,
                    'is_registered': False,
                    'orders': [],
                    'reviews': [rev],
                    'total_spent': 0,
                    'orders_count': 0,
                    'reviews_count': 1,
                    'last_active': rev.created_at,
                    'address': '',
                    'city': '',
                }

    # Finalize counts
    customers_list = list(customers_map.values())
    for c in customers_list:
        c['orders_count'] = len(c['orders'])
        c['reviews_count'] = len(c['reviews'])

    # Filtering
    if customer_type == 'registered':
        customers_list = [c for c in customers_list if c['is_registered']]
    elif customer_type == 'guest':
        customers_list = [c for c in customers_list if not c['is_registered']]

    if search_query:
        q_lower = search_query.lower()
        customers_list = [
            c for c in customers_list
            if q_lower in c['name'].lower()
            or (c['phone'] and q_lower in c['phone'].lower())
            or (c['email'] and q_lower in c['email'].lower())
        ]

    # Sort by last_active descending
    customers_list.sort(key=lambda x: x['last_active'], reverse=True)

    # Summary metrics
    total_customers_count = len(customers_map)
    total_revenue = sum(c['total_spent'] for c in customers_map.values())
    total_reviews_count = Review.objects.count()
    active_buyers_count = sum(1 for c in customers_map.values() if c['orders_count'] > 0)

    context = {
        'customers': customers_list,
        'search_query': search_query,
        'selected_type': customer_type,
        'total_customers_count': total_customers_count,
        'total_revenue': total_revenue,
        'total_reviews_count': total_reviews_count,
        'active_buyers_count': active_buyers_count,
    }
    return render(request, 'dashboard/customers/list.html', context)


@staff_member_required
def customer_detail(request, customer_key):
    """
    Detailed 360-degree customer profile:
    Shows customer personal info, order history, purchased iPhone devices, and submitted reviews.
    """
    user = None
    phone = None
    
    if customer_key.startswith('u-'):
        user_id = customer_key.split('-')[1]
        user = get_object_or_404(User, id=user_id)
        orders = Order.objects.filter(user=user).prefetch_related('items').order_by('-created_at')
        reviews = Review.objects.filter(user=user).select_related('product', 'product__model').order_by('-created_at')
        name = user.get_full_name() or user.username
        email = user.email
        phone = orders.first().phone if orders.exists() else ''
        joined_date = user.date_joined
        is_registered = True
        address = orders.first().delivery_address if orders.exists() else ''
        city = orders.first().get_city_display() if orders.exists() else ''
    elif customer_key.startswith('p-'):
        phone = customer_key[2:]
        orders = Order.objects.filter(phone=phone).prefetch_related('items').order_by('-created_at')
        reviews = Review.objects.filter(customer_phone=phone).select_related('product', 'product__model').order_by('-created_at')
        first_order = orders.first()
        name = first_order.full_name if first_order else (reviews.first().customer_name if reviews.exists() else phone)
        email = first_order.email if first_order and first_order.email else (reviews.first().customer_email if reviews.exists() else '')
        joined_date = orders.last().created_at if orders.exists() else (reviews.last().created_at if reviews.exists() else timezone.now())
        is_registered = False
        address = first_order.delivery_address if first_order else ''
        city = first_order.get_city_display() if first_order else ''
    elif customer_key.startswith('o-'):
        order_id = customer_key.split('-')[1]
        order = get_object_or_404(Order, id=order_id)
        orders = Order.objects.filter(id=order.id).prefetch_related('items')
        reviews = Review.objects.none()
        name = order.full_name
        email = order.email
        phone = order.phone
        joined_date = order.created_at
        is_registered = False
        address = order.delivery_address
        city = order.get_city_display()
    else:
        messages.error(request, "Customer not found.")
        return redirect('dashboard:customer_list')

    # Purchased Items snapshot
    purchased_items = OrderItem.objects.filter(order__in=orders).select_related('order', 'product', 'product__model').order_by('-order__created_at')

    total_spent = orders.exclude(order_status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = orders.count()
    delivered_orders = orders.filter(order_status='delivered').count()
    total_reviews = reviews.count()

    context = {
        'customer_key': customer_key,
        'customer_name': name,
        'customer_email': email,
        'customer_phone': phone,
        'customer_address': address,
        'customer_city': city,
        'joined_date': joined_date,
        'is_registered': is_registered,
        'user_obj': user,
        'orders': orders,
        'purchased_items': purchased_items,
        'reviews': reviews,
        'total_spent': total_spent,
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'total_reviews': total_reviews,
    }
    return render(request, 'dashboard/customers/detail.html', context)


# ==============================================================================
# REVIEWS MANAGEMENT & MODERATION
# ==============================================================================

@staff_member_required
def review_list(request):
    """
    Global Product Reviews Manager & Moderation.
    """
    reviews = Review.objects.select_related('product', 'product__model', 'user').order_by('-created_at')
    
    rating_filter = request.GET.get('rating')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('q', '').strip()

    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    if status_filter == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif status_filter == 'pending':
        reviews = reviews.filter(is_approved=False)

    if search_query:
        reviews = reviews.filter(
            Q(customer_name__icontains=search_query) |
            Q(customer_phone__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(comment__icontains=search_query) |
            Q(product__sku__icontains=search_query) |
            Q(product__title__icontains=search_query)
        )

    counts = {
        'all': Review.objects.count(),
        'approved': Review.objects.filter(is_approved=True).count(),
        'pending': Review.objects.filter(is_approved=False).count(),
        'five_star': Review.objects.filter(rating=5).count(),
    }

    context = {
        'reviews': reviews,
        'selected_rating': rating_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'counts': counts,
    }
    return render(request, 'dashboard/reviews/list.html', context)


@staff_member_required
def review_toggle_approval(request, review_id):
    """
    Toggle publication approval for a customer review.
    """
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = not review.is_approved
    review.save(update_fields=['is_approved'])
    
    status_text = "Approved and published on store" if review.is_approved else "Hidden from store"
    messages.success(request, f"Review #{review.id} by {review.customer_name} is now {status_text}.")
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:review_list')


@staff_member_required
def review_delete(request, review_id):
    """
    Delete a customer review.
    """
    review = get_object_or_404(Review, id=review_id)
    customer = review.customer_name
    review.delete()
    messages.success(request, f"Review by {customer} has been permanently deleted.")
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard:review_list')

