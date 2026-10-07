from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/export/csv/', views.order_export_csv, name='order_export_csv'),
    
    # Products & Inventory
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:product_id>/status/<str:new_status>/', views.product_toggle_status, name='product_toggle_status'),
    path('products/images/<int:image_id>/delete/', views.product_image_delete, name='product_image_delete'),

    # FAQs
    path('faqs/', views.faq_list, name='faq_list'),
    path('faqs/create/', views.faq_create, name='faq_create'),
    path('faqs/<int:faq_id>/edit/', views.faq_edit, name='faq_edit'),
    path('faqs/<int:faq_id>/delete/', views.faq_delete, name='faq_delete'),

    # Settings
    path('settings/', views.store_settings_view, name='settings'),
]
