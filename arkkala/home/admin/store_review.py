from django.contrib import admin
from home.models import StoreReview

@admin.register(StoreReview)
class StoreReviewAdmin(admin.ModelAdmin):
    list_display: tuple = ('user_name', 'is_active', 'created_at')
    list_editable: tuple = ('is_active',)