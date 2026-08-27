from django.contrib import admin
from home.models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display: tuple = ('question', 'order', 'is_active')
    list_editable: tuple = ('order', 'is_active')