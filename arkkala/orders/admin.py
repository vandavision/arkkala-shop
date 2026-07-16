from typing import Any
from django.contrib import admin
from django.http import HttpRequest

from .models import ShippingMethod, Coupon, Order, OrderItem, Cart, OrderRequest
from .services.order import OrderRequestService


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'guest_id', 'created_at')
    search_fields = ('user__username', 'guest_id')


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'request_type', 'status', 'created_at')
    list_filter = ('request_type', 'status', 'created_at')
    search_fields = ('order__uuid',)
    list_editable = ('status',)
    
    def save_model(self, request: HttpRequest, obj: OrderRequest, form: Any, change: bool) -> None:
        super().save_model(request, obj, form, change)
        
        if obj.status == OrderRequest.StatusChoices.APPROVED:
            OrderRequestService.process_approved_request(obj)


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