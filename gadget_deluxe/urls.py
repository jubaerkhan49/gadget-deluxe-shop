from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
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
