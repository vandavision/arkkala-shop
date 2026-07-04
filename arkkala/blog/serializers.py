"""
Serializers for the Blog App.
Handles data transformation and validation for blog models.
"""
from typing import Any, Dict, List, Optional
from rest_framework import serializers
from rest_framework.request import Request
from .models import Category, Tag, Post, Comment


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for the Blog Category model."""
    
    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Blog Tag model."""
    
    class Meta:
        model = Tag
        fields = ['uuid', 'title', 'slug']


class PostSeoSerializer(serializers.ModelSerializer):
    """
    SEO fields Serializer for Blog Post.
    Utilizes platform_seo package features for rich snippets and OpenGraph.
    """
    json_ld = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()
    meta_keywords = serializers.JSONField(source='keywords', read_only=True)
    canonical_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['meta_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'json_ld']

    def get_json_ld(self, obj: Post) -> Dict[str, Any]:
        """Get generated JSON-LD from Post model."""
        return obj.generate_json_ld() if hasattr(obj, 'generate_json_ld') else {}

    def get_og_image_url(self, obj: Post) -> Optional[str]:
        """Construct the absolute URL for the OpenGraph image."""
        if hasattr(obj, 'og_image') and obj.og_image:
            request: Optional[Request] = self.context.get('request')
            return request.build_absolute_uri(obj.og_image.url) if request else obj.og_image.url
        return None
        
    def get_canonical_url(self, obj: Post) -> str:
        """
        Construct the canonical URL for the post.
        Uses 'slug' instead of 'id' for SEO standard compliance.
        """
        request: Optional[Request] = self.context.get('request')
        path: str = f"/blog/{obj.slug}/"
        if request:
            return request.build_absolute_uri(path)
        return path


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for Blog Comments."""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['uuid', 'user_name', 'body', 'created_at']
        
    def get_user_name(self, obj: Comment) -> str:
        """Get User Full Name or return anonymous string."""
        if obj.user and obj.user.get_full_name():
            return obj.user.get_full_name()
        return "کاربر ناشناس"


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for listing Blog Posts (without full body and comments)."""
    category = BlogCategorySerializer(read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Post
        fields = [
            'uuid', 'title', 'slug', 'category', 'author_name', 'image', 
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
            'uuid', 'title', 'slug', 'category', 'tags', 'author_name', 'image', 
            'short_description', 'body', 'view_count', 'read_time', 
            'comments', 'seo', 'created_at'
        ]

    def get_comments(self, obj: Post) -> List[Dict[str, Any]]:
        """Return approved comments for the specific post."""
        approved_comments = obj.comments.filter(is_approved=True)
        return BlogCommentSerializer(approved_comments, many=True).data