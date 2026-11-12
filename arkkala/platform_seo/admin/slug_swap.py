from django.contrib import admin

from platform_seo.models import SlugSwap


@admin.register(SlugSwap)
class SlugSwapAdmin(admin.ModelAdmin):
    list_display = ("new_slug", "old_slug", "redirect_type", "related_object_display")

    list_editable = ("redirect_type",)

    readonly_fields = (
        "old_slug",
        "new_slug",
        "content_type",
        "object_id",
        "related_object_display",
    )

    fields = (
        "old_slug",
        "new_slug",
        "redirect_type",
        "content_type",
        "related_object_display",
    )

    search_fields = (
        "old_slug",
        "new_slug",
    )

    @admin.display(description="موجودیت مرتبط")
    def related_object_display(self, obj: SlugSwap) -> str:
        """Safely resolves related objects for both integer-PK and UUID-PK models."""
        if not obj.content_type:
            return "-"
        model_class = obj.content_type.model_class()
        if not model_class:
            return "-"
        try:
            if hasattr(model_class, "slug"):
                instance = model_class.objects.filter(slug=obj.new_slug).first()
                if instance:
                    return str(instance)
            if obj.object_id:
                instance = model_class.objects.filter(pk=obj.object_id).first()
                if instance:
                    return str(instance)
        except Exception:
            pass
        return f"{obj.content_type.name} ({obj.new_slug})"