from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom Admin Title & Header
admin.site.site_header = "Gadget Deluxe Administration"
admin.site.site_title = "Gadget Deluxe Admin Portal"
admin.site.index_title = "Shop & Inventory Management"
