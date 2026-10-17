from django.contrib import admin
from django.urls import path, include, re_path, reverse
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


def admin_login_redirect(request, **kwargs):
    """
    Redirects staff members to the custom Shop Admin (/shop-admin/) instead of
    Django's internal admin index, while preserving any specific next parameter.
    """
    if request.user.is_authenticated and request.user.is_staff:
        next_url = request.GET.get('next') or request.POST.get('next')
        if not next_url or next_url in ('/admin/', '/admin', reverse('admin:index')):
            return redirect('dashboard:home')
        return redirect(next_url)

    extra_context = kwargs.get('extra_context') or {}
    if 'next' not in extra_context:
        req_next = request.GET.get('next')
        if not req_next or req_next in ('/admin/', '/admin', reverse('admin:index')):
            extra_context['next'] = reverse('dashboard:home')
    kwargs['extra_context'] = extra_context
    return admin.site.login(request, **kwargs)


urlpatterns = [
    path('admin/login/', admin_login_redirect, name='admin_login'),
    path('admin/', admin.site.urls),
    path('shop-admin/', include('dashboard.urls', namespace='dashboard')),
    path('', include('store.urls', namespace='store')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('i18n/', include('django.conf.urls.i18n')),
    # Media file serving (handles media both on Render in production and locally)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom Admin Title & Header
admin.site.site_header = "Gadget Deluxe Administration"
admin.site.site_title = "Gadget Deluxe Admin Portal"
admin.site.index_title = "Shop & Inventory Management"
