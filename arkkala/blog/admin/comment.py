# arkkala/blog/admin/comment.py
from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from blog.models.comment import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment."""
    list_display = ('post', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('body', 'user__first_name', 'user__last_name', 'user__phone_number')
    actions = ['approve_comments']
    list_editable = ('is_approved',)

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Approves selected comments in bulk."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} نظر با موفقیت تایید شد.")