from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from store.models import Product, StoreSettings
from .models import Order, OrderItem
from .forms import CheckoutForm, OrderTrackSearchForm
from .cart import Cart
from decimal import Decimal


def cart_detail(request):
    """
    Display shopping cart with price breakdown and stock validation.
    """
    cart = Cart(request)
    removed_items = cart.validate_cart()
    if removed_items:
        messages.warning(
            request, 
            f"Note: Some items ({', '.join(removed_items)}) were removed from your cart because they were just sold."
        )

    settings = StoreSettings.get_settings()
    subtotal = cart.get_total_price()
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'delivery_inside': settings.delivery_charge_inside_dhaka,
        'delivery_outside': settings.delivery_charge_outside_dhaka,
    }
    return render(request, 'orders/cart_detail.html', context)


def cart_add(request, product_id):
    """
    Add a unique iPhone listing to the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if product.status != 'available':
        messages.error(request, "Sorry, this specific iPhone listing is currently unavailable or sold out.")
        return redirect('store:product_detail', slug=product.slug)

    cart.add(product=product, quantity=1)

    # Check for 'buy_now' parameter
    if request.GET.get('buy_now') == '1' or request.POST.get('buy_now') == '1':
        return redirect('orders:checkout')

    messages.success(request, f"Added {product.title} to your cart.")
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'orders:cart_detail'
    return redirect(next_url)


def cart_remove(request, product_id):
    """
    Remove an iPhone listing from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed {product.title} from your cart.")
    return redirect('orders:cart_detail')


def cart_clear(request):
    """
    Clear all items from the cart.
    """
    cart = Cart(request)
    cart.clear()
    messages.info(request, "Your cart has been cleared.")
    return redirect('orders:cart_detail')


def checkout(request):
    """
    Simple, secure checkout for both registered users and guest customers.
    """
    cart = Cart(request)

    # If cart is empty, redirect back to catalog
    if len(cart) == 0:
        messages.warning(request, "Your cart is currently empty. Please select an iPhone first.")
        return redirect('store:product_list')

    # Validate stock
    removed = cart.validate_cart()
    if removed:
        messages.error(request, f"Some items were removed as they are no longer available: {', '.join(removed)}")
        return redirect('orders:cart_detail')

    settings = StoreSettings.get_settings()
    subtotal = cart.get_total_price()

    initial_data = {}
    if request.user.is_authenticated:
        initial_data['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        initial_data['email'] = request.user.email

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Re-verify product availability atomically with row locking
                cart_product_ids = [item['product'].id for item in cart]
                locked_products = Product.objects.select_for_update().filter(id__in=cart_product_ids)
                
                # Verify all are still available
                unavailable = [p for p in locked_products if p.status != 'available']
                if unavailable:
                    messages.error(request, "Sorry, one of the phones in your cart was just reserved by another customer. Please review your cart.")
                    cart.validate_cart()
                    return redirect('orders:cart_detail')

                # Calculate delivery charge
                city = form.cleaned_data['city']
                delivery_charge = settings.delivery_charge_inside_dhaka if city == 'inside_dhaka' else settings.delivery_charge_outside_dhaka
                
                # Total calculation server-side (never trusting client-side price)
                calculated_subtotal = sum(p.price for p in locked_products)
                total_amount = calculated_subtotal + delivery_charge

                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                
                order.subtotal = calculated_subtotal
                order.delivery_charge = delivery_charge
                order.total_amount = total_amount
                
                # Payment status determination
                if order.payment_method == 'cod':
                    order.payment_status = 'unpaid'
                elif order.payment_trx_id:
                    order.payment_status = 'pending_verification'
                else:
                    order.payment_status = 'unpaid'

                order.order_status = 'pending'
                order.save()

                # Create OrderItems and mark products as reserved/sold
                for product in locked_products:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_title=product.title,
                        product_sku=product.sku,
                        product_model=product.model.name,
                        product_storage=product.storage,
                        product_color=product.color,
                        product_condition=product.get_condition_display(),
                        product_battery_health=product.battery_health,
                        price=product.price,
                        quantity=1
                    )
                    # Mark physical device as reserved/sold
                    product.status = 'reserved'
                    product.save(update_fields=['status'])

                # Clear cart
                cart.clear()

                messages.success(request, f"🎉 Order placed successfully! Your Order ID is #{order.order_number}")
                return redirect('orders:order_success', token=order.tracking_token)
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'subtotal': subtotal,
        'settings': settings,
    }
    return render(request, 'orders/checkout.html', context)


def order_success(request, token):
    """
    Order confirmation screen with receipt details and payment instructions.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items'), tracking_token=token)
    settings = StoreSettings.get_settings()
    
    context = {
        'order': order,
        'settings': settings,
    }
    return render(request, 'orders/order_success.html', context)


def track_order(request, token=None):
    """
    Order tracking page for both guests and registered users.
    Supports tracking via direct token or by Order Number + Phone.
    """
    order = None
    search_performed = False

    if token:
        order = get_object_or_404(Order.objects.prefetch_related('items'), tracking_token=token)
        search_performed = True
        form = OrderTrackSearchForm(initial={'order_number': order.order_number, 'phone': order.phone})
    elif request.method == 'GET' and ('order_number' in request.GET or 'phone' in request.GET):
        form = OrderTrackSearchForm(request.GET)
        if form.is_valid():
            order_num = form.cleaned_data['order_number'].upper().strip()
            phone = form.cleaned_data['phone']
            search_performed = True

            try:
                order = Order.objects.prefetch_related('items').get(
                    order_number=order_num,
                    phone=phone
                )
            except Order.DoesNotExist:
                messages.error(request, "No order found matching this Order Number and Phone. Please check your information.")
    else:
        form = OrderTrackSearchForm()

    context = {
        'form': form,
        'order': order,
        'search_performed': search_performed,
    }
    return render(request, 'orders/track_order.html', context)
