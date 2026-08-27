from django.contrib import admin
from home.models import Story

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display: tuple = ('title', 'is_active', 'created_at')
    list_editable: tuple = ('is_active',)