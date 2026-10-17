from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import translation
from django.http import HttpResponseRedirect
from .models import IPhoneModel, Product, FAQ, StoreSettings, Review
from orders.models import Order, OrderItem


def home(request):
    """
    Simple, elegant homepage focused exclusively on quality used iPhones.
    """
    featured_products = Product.objects.filter(
        status='available', 
        featured=True
    ).select_related('model')[:6]

    # If fewer than 6 featured, fetch available products
    if featured_products.count() < 4:
        all_available = Product.objects.filter(
            status='available'
        ).select_related('model')[:8]
    else:
        all_available = Product.objects.filter(
            status='available'
        ).select_related('model')[:8]

    models_list = IPhoneModel.objects.filter(is_active=True).order_by('order')
    faqs_preview = FAQ.objects.filter(is_active=True).order_by('order')[:4]
    
    # Model counts for filter badges
    model_slug = request.GET.get('model')
    active_products = Product.objects.filter(status='available')
    if model_slug:
        active_products = active_products.filter(model__slug=model_slug)

    context = {
        'featured_products': featured_products,
        'recent_products': active_products[:8],
        'models_list': models_list,
        'selected_model': model_slug,
        'faqs_preview': faqs_preview,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """
    Full catalogue filterable by iPhone Model, Storage, and Condition.
    """
    queryset = Product.objects.filter(status__in=['available', 'reserved']).select_related('model')

    # Filtering
    model_slug = request.GET.get('model')
    storage = request.GET.get('storage')
    condition = request.GET.get('condition')
    sort_by = request.GET.get('sort', '-created_at')
    query = request.GET.get('q', '').strip()

    if model_slug:
        queryset = queryset.filter(model__slug=model_slug)
    if storage:
        queryset = queryset.filter(storage=storage)
    if condition:
        queryset = queryset.filter(condition=condition)
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(model__name__icontains=query) |
            Q(color__icontains=query) |
            Q(sku__icontains=query)
        )

    # Sorting
    if sort_by == 'price_low':
        queryset = queryset.order_by('price')
    elif sort_by == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort_by == 'battery':
        queryset = queryset.order_by('-battery_health')
    else:
        queryset = queryset.order_by('-created_at')

    models_list = IPhoneModel.objects.filter(is_active=True).order_by('order')

    context = {
        'products': queryset,
        'models_list': models_list,
        'selected_model': model_slug,
        'selected_storage': storage,
        'selected_condition': condition,
        'selected_sort': sort_by,
        'search_query': query,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """
    Detailed product listing page showing battery health, SIM, condition, photos.
    """
    product = get_object_or_404(
        Product.objects.select_related('model').prefetch_related('images'), 
        slug=slug
    )

    # Related listings of same or similar models
    related_products = Product.objects.filter(
        model=product.model, 
        status='available'
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


def submit_review(request, product_id):
    """
    Handle customer review submission for a specific iPhone listing.
    """
    if request.method != 'POST':
        return redirect('store:home')

    product = get_object_or_404(Product, id=product_id)
    try:
        rating = int(request.POST.get('rating', 5))
    except (ValueError, TypeError):
        rating = 5
    rating = max(1, min(5, rating))
    
    name = request.POST.get('customer_name', '').strip()
    phone = request.POST.get('customer_phone', '').strip()
    email = request.POST.get('customer_email', '').strip()
    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()

    if not name or not comment:
        messages.error(request, "Please enter your name and a brief review message.")
        return redirect('store:product_detail', slug=product.slug)

    # Check for verified purchase
    is_verified = False
    if request.user.is_authenticated:
        if OrderItem.objects.filter(order__user=request.user, product=product).exists() or Order.objects.filter(user=request.user).exists():
            is_verified = True
    elif phone:
        clean_p = phone.replace(' ', '').replace('-', '')
        if clean_p.startswith('+88'):
            clean_p = clean_p[3:]
        elif clean_p.startswith('88'):
            clean_p = clean_p[2:]
        if Order.objects.filter(phone__icontains=clean_p).exists():
            is_verified = True

    Review.objects.create(
        product=product,
        user=request.user if request.user.is_authenticated else None,
        customer_name=name,
        customer_phone=phone,
        customer_email=email,
        rating=rating,
        title=title,
        comment=comment,
        is_verified_purchase=is_verified,
        is_approved=True,
    )

    messages.success(request, "🎉 Thank you! Your review has been published.")
    return redirect('store:product_detail', slug=product.slug)


def faq_view(request):
    """
    Dedicated FAQ page focused specifically on used iPhones.
    """
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    # Group FAQs by category
    categories = {
        'quality': {
            'title_en': 'Quality, Testing & Authenticity',
            'title_bn': 'মান নিয়ন্ত্রণ, টেস্টিং ও সততা',
            'items': []
        },
        'battery': {
            'title_en': 'Battery Health & Warranty',
            'title_bn': 'ব্যাটারি হেলথ ও ওয়ারেন্টি',
            'items': []
        },
        'order': {
            'title_en': 'Ordering & Delivery Details',
            'title_bn': 'অর্ডার ও ডেলিভারি তথ্য',
            'items': []
        },
        'payment': {
            'title_en': 'Payment Methods & Security',
            'title_bn': 'পেমেন্ট মাধ্যম ও নিরাপত্তা',
            'items': []
        },
    }

    for faq in faqs:
        cat_key = faq.category if faq.category in categories else 'quality'
        categories[cat_key]['items'].append(faq)

    context = {
        'faq_categories': categories,
    }
    return render(request, 'store/faq.html', context)


def switch_language(request, lang_code):
    """
    Switch language between 'en' and 'bn'.
    """
    next_url = request.META.get('HTTP_REFERER') or '/'
    response = HttpResponseRedirect(next_url)
    if lang_code in ['en', 'bn']:
        translation.activate(lang_code)
        request.session['_language'] = lang_code
        response.set_cookie('django_language', lang_code)
    return response
