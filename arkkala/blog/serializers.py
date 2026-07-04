"""
Serializers for the Blog App.
"""
from typing import Any, Dict, List
from rest_framework import serializers
from .models import Category, Tag, Post, Comment


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for Blog Category."""
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Blog Tags."""
    class Meta:
        model = Tag
        fields = ['id', 'title', 'slug']


class PostSeoSerializer(serializers.ModelSerializer):
    """SEO fields Serializer for Blog Post."""
    json_ld = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['meta_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'json_ld']

    def get_json_ld(self, obj: Post) -> Dict[str, Any]:
        """Get generated JSON-LD from Post model."""
        return obj.generate_json_ld() if hasattr(obj, 'generate_json_ld') else {}

    def get_og_image_url(self, obj: Post) -> str | None:
        """Get OG Image URL."""
        return obj.og_image.url if hasattr(obj, 'og_image') and obj.og_image else None


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for Blog Comments."""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'body', 'created_at']
        
    def get_user_name(self, obj: Comment) -> str:
        """Get User Full Name or return anonymous string."""
        return obj.user.get_full_name() if obj.user and obj.user.get_full_name() else "کاربر ناشناس"


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for listing Blog Posts (without full body and comments)."""
    category = BlogCategorySerializer(read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'category', 'author_name', 'image', 
            'short_description', 'view_count', 'read_time', 'created_at'
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Blog Post view."""
    category = BlogCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    comments = serializers.SerializerMethodField()
    seo = PostSeoSerializer(source='*', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'category', 'tags', 'author_name', 'image', 
            'short_description', 'body', 'view_count', 'read_time', 
            'comments', 'seo', 'created_at'
        ]

    def get_comments(self, obj: Post) -> List[Dict[str, Any]]:
        """Return approved comments for the post."""
        approved_comments = obj.comments.filter(is_approved=True)
        return BlogCommentSerializer(approved_comments, many=True).data