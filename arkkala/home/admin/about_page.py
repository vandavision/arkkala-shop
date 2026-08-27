from django.contrib import admin
from home.models import AboutPage

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display: tuple = ('title', 'is_active', 'created_at')