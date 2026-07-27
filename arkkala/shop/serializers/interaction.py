# shop/serializers/interaction.py
from typing import Optional
from rest_framework import serializers
from rest_framework.request import Request
from shop.models.interaction import Comment, Question


class QuestionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['uuid', 'user_name', 'text', 'answer_text', 'created_at']

    def get_user_name(self, obj: Question) -> str:
        if obj.user and obj.user.get_full_name():
            return obj.user.get_full_name()
        return obj.name or "کاربر مهمان"


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['uuid', 'user_name', 'body', 'rating', 'created_at']
        
    def get_user_name(self, obj: Comment) -> str:
        if obj.user and obj.user.get_full_name():
            return obj.user.get_full_name()
        return "کاربر ناشناس"


class UserCommentSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_image = serializers.SerializerMethodField()
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'product_title', 'product_slug', 'product_image', 'body', 'rating', 'is_approved', 'created_at']

    def get_product_image(self, obj: Comment) -> Optional[str]:
        if not obj.product:
            return None
        main_img = obj.product.gallery.filter(is_main=True).first() or obj.product.gallery.first()
        if main_img and main_img.image:
            request: Optional[Request] = self.context.get('request')
            return request.build_absolute_uri(main_img.image.url) if request else main_img.image.url
        return None