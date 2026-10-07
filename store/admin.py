from django.contrib import admin
from django.utils.html import format_html
from .models import IPhoneModel, Product, ProductImage, FAQ, StoreSettings


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'order')


@admin.register(IPhoneModel)
class IPhoneModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_year', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 
        'thumbnail_preview',
        'title', 
        'model', 
        'storage', 
        'color', 
        'condition_badge', 
        'battery_badge', 
        'price_formatted', 
        'status', 
        'featured',
        'created_at'
    )
    list_filter = ('model', 'storage', 'condition', 'status', 'featured', 'created_at')
    search_fields = ('sku', 'title', 'color', 'masked_imei')
    list_editable = ('status', 'featured')
    inlines = [ProductImageInline]
    readonly_fields = ('sku', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Device Identification', {
            'fields': ('sku', 'title', 'title_bn', 'slug', 'model', 'origin_region', 'masked_imei')
        }),
        ('Specifications & Condition', {
            'fields': (
                'storage', 
                ('color', 'color_bn'), 
                'condition', 
                'battery_health', 
                'sim_type'
            )
        }),
        ('Pricing & Status', {
            'fields': (
                ('price', 'original_price'), 
                'status', 
                'featured', 
                'warranty_info'
            )
        }),
        ('Visuals & Description', {
            'fields': (
                'primary_image', 
                'description', 
                'description_bn'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.primary_image:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; object-fit: contain; border-radius: 6px; background: #f4f4f5;" />',
                obj.primary_image.url
            )
        return "—"
    thumbnail_preview.short_description = "Image"

    def price_formatted(self, obj):
        return f"৳{obj.price:,}"
    price_formatted.short_description = "Price"

    def condition_badge(self, obj):
        colors = {
            'like_new': '#10B981',
            'excellent': '#3B82F6',
            'good': '#F59E0B'
        }
        color = colors.get(obj.condition, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_condition_display()
        )
    condition_badge.short_description = "Condition"

    def battery_badge(self, obj):
        color = '#10B981' if obj.battery_health >= 90 else '#F59E0B'
        return format_html(
            '<span style="color: {}; font-weight: bold;">🔋 {}%</span>',
            color,
            obj.battery_health
        )
    battery_badge.short_description = "Battery"

    def status_badge(self, obj):
        colors = {
            'available': '#10B981',
            'reserved': '#F59E0B',
            'sold': '#EF4444'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_en', 'category', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('question_en', 'question_bn', 'answer_en', 'answer_bn')
    list_editable = ('order', 'is_active')


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'phone_number', 'email', 'delivery_charge_inside_dhaka', 'delivery_charge_outside_dhaka')
    
    def has_add_permission(self, request):
        # Only allow 1 instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
