from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from shop.models.interaction import Comment, Question, UserProductHistory

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display: tuple = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter: tuple = ('is_approved', 'rating')
    search_fields: tuple = ('body', 'product__title')
    autocomplete_fields: tuple = ('product', 'user')
    list_editable: tuple = ('is_approved',)
    readonly_fields: tuple = ('uuid', 'created_at', 'modified_at')
    actions: list = ['approve_comments', 'reject_comments']

    fieldsets: tuple = (
        (None, {'fields': ('product', 'user', 'body', 'rating', 'is_approved')}),
        ('اطلاعات سیستمی', {'fields': ('uuid', 'created_at', 'modified_at'), 'classes': ('collapse',)}),
    )

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated: int = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} نظر با موفقیت تایید شد.")

    @admin.action(description='رد نظرات انتخاب شده')
    def reject_comments(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated: int = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} نظر رد شد.")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display: tuple = ('product', 'get_author_name', 'is_approved', 'has_answer', 'created_at')
    list_filter: tuple = ('is_approved', 'created_at')
    search_fields: tuple = ('text', 'answer_text', 'product__title', 'name')
    autocomplete_fields: tuple = ('product', 'user')
    list_editable: tuple = ('is_approved',)
    readonly_fields: tuple = ('uuid', 'created_at', 'modified_at')
    actions: list = ['approve_questions']

    fieldsets: tuple = (
        ('اطلاعات پرسش', {'fields': ('product', 'user', 'name', 'text', 'is_approved')}),
        ('پاسخ (مولد AEO)', {'fields': ('answer_text',)}),
        ('اطلاعات سیستمی', {'fields': ('uuid', 'created_at', 'modified_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='پرسشگر')
    def get_author_name(self, obj: Question) -> str:
        if obj.user:
            return obj.user.get_full_name() or str(obj.user.email)
        return obj.name or 'مهمان'

    @admin.display(description='پاسخ داده شده؟', boolean=True)
    def has_answer(self, obj: Question) -> bool:
        return bool(obj.answer_text and obj.answer_text.strip())

    @admin.action(description='تایید پرسش‌ها')
    def approve_questions(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated: int = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} پرسش با موفقیت تایید شد.")

@admin.register(UserProductHistory)
class UserProductHistoryAdmin(admin.ModelAdmin):
    list_display: tuple = ('user', 'product', 'view_count', 'modified_at')
    list_filter: tuple = ('modified_at',)
    search_fields: tuple = ('user__username', 'product__title')
    autocomplete_fields: tuple = ('user', 'product')
    readonly_fields: tuple = ('uuid', 'created_at', 'modified_at')