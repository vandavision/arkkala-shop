"""
Admin Interface for Orders.
"""
from django.contrib import admin
from .models import ShippingMethod, Coupon, Order, OrderItem, Cart

admin.site.register(Cart)

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_cost', 'is_pay_on_delivery', 'is_active')
    list_filter = ('is_pay_on_delivery', 'is_active')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_to', 'usage_limit', 'used_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'unit_price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'guest_phone', 'status', 'payable_amount', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'shipping_method')
    search_fields = ('user__username', 'guest_phone', 'tracking_code')
    readonly_fields = ('total_items_amount', 'discount_amount', 'shipping_cost', 'payable_amount')
    inlines = [OrderItemInline]
    fieldsets = (
        ('اطلاعات کاربر و وضعیت', {
            'fields': ('user', 'guest_phone', 'status', 'is_paid', 'tracking_code')
        }),
        ('اطلاعات مالی', {
            'fields': ('total_items_amount', 'discount_amount', 'shipping_cost', 'payable_amount')
        }),
        ('ارسال و تخفیف', {
            'fields': ('shipping_method', 'coupon')
        }),
        ('آدرس پستی', {
            'fields': ('title', 'country', 'province', 'city', 'postal_address', 'postal_code', 'plaque', 'building_unit')
        }),
    )