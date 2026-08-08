from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from blog.models.comment import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display: tuple = ('post', 'user', 'is_approved', 'created_at')
    list_filter: tuple = ('is_approved', 'created_at')
    search_fields: tuple = ('body', 'user__first_name', 'user__last_name', 'user__phone_number')
    actions: list = ['approve_comments']
    list_editable: tuple = ('is_approved',)
    readonly_fields: tuple = ('uuid', 'created_at', 'modified_at')
    autocomplete_fields: tuple = ('post', 'user')

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated: int = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} نظر با موفقیت تایید شد.")