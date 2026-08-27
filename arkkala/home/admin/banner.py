from django.contrib import admin
from home.models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display: tuple = ('title', 'position', 'is_active')
    list_editable: tuple = ('is_active',)