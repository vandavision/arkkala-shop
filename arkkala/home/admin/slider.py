from django.contrib import admin
from home.models import Slider

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display: tuple = ('title', 'order', 'is_active')
    list_editable: tuple = ('order', 'is_active')