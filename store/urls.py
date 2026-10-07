from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('iphones/', views.product_list, name='product_list'),
    path('iphones/<slug:slug>/', views.product_detail, name='product_detail'),
    path('faq/', views.faq_view, name='faq'),
    path('language/<str:lang_code>/', views.switch_language, name='switch_language'),
]
