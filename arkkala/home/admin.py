"""
Admin configuration for Home App.
"""
from django.contrib import admin
from .models import Story, Slider, Banner, StoreReview

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_editable = ('is_active',)

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_active')
    list_editable = ('is_active',)

@admin.register(StoreReview)
class StoreReviewAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'is_active', 'created_at')
    list_editable = ('is_active',)