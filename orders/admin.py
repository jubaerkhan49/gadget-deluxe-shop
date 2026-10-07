from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product', 
        'product_title', 
        'product_sku', 
        'product_model', 
        'product_storage', 
        'product_color', 
        'product_condition', 
        'product_battery_health', 
        'price', 
        'quantity', 
        'total_price'
    )
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'phone',
        'total_amount_formatted',
        'payment_method_badge',
        'payment_status',
        'order_status',
        'created_at'
    )
    list_filter = (
        'order_status', 
        'payment_status', 
        'payment_method', 
        'city', 
        'created_at'
    )
    search_fields = (
        'order_number', 
        'full_name', 
        'phone', 
        'email', 
        'payment_sender_number', 
        'payment_trx_id'
    )
    list_editable = ('order_status', 'payment_status')
    inlines = [OrderItemInline]
    readonly_fields = (
        'order_number', 
        'tracking_token', 
        'subtotal', 
        'delivery_charge', 
        'total_amount', 
        'created_at', 
        'updated_at'
    )

    fieldsets = (
        ('Order Overview', {
            'fields': (
                ('order_number', 'tracking_token'),
                ('order_status', 'payment_status'),
                ('subtotal', 'delivery_charge', 'total_amount')
            )
        }),
        ('Customer & Delivery Information', {
            'fields': (
                'user',
                ('full_name', 'phone'),
                'email',
                'delivery_address',
                'city',
                'delivery_notes'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method',
                ('payment_sender_number', 'payment_trx_id'),
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_amount_formatted(self, obj):
        return f"৳{obj.total_amount:,}"
    total_amount_formatted.short_description = "Total"

    def payment_method_badge(self, obj):
        return obj.get_payment_method_display().split('/')[0].strip()
    payment_method_badge.short_description = "Payment"

    def payment_status_badge(self, obj):
        colors = {
            'unpaid': '#EF4444',
            'pending_verification': '#F59E0B',
            'paid': '#10B981',
            'failed': '#DC2626',
            'refunded': '#6B7280'
        }
        color = colors.get(obj.payment_status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_payment_status_display().split('/')[0].strip()
        )
    payment_status_badge.short_description = "Payment Status"

    def order_status_badge(self, obj):
        colors = {
            'pending': '#F59E0B',
            'confirmed': '#3B82F6',
            'processing': '#8B5CF6',
            'shipped': '#6366F1',
            'out_for_delivery': '#EC4899',
            'delivered': '#10B981',
            'cancelled': '#EF4444'
        }
        color = colors.get(obj.order_status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_order_status_display().split('/')[0].strip()
        )
    order_status_badge.short_description = "Order Status"
