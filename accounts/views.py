from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomerRegistrationForm, CustomerLoginForm
from orders.models import Order


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Gadget Deluxe, {user.first_name or user.username}!")
            return redirect('store:home')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:home')
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if not next_url or next_url in ('accounts:profile', '/account/profile/'):
                if user.is_staff:
                    return redirect('dashboard:home')
                return redirect('accounts:profile')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password. Please try again.")
    else:
        form = CustomerLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('store:home')


@login_required
def profile_view(request):
    user_orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    
    context = {
        'orders': user_orders,
    }
    return render(request, 'accounts/profile.html', context)
