from django.contrib import admin
from django.http import HttpRequest
from home.models import SiteSetting

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display: tuple = ('site_name', 'phone_number')
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)