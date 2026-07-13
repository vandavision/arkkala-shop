"""
Serializers for the Blog App.
Handles data transformation and validation for blog models.
Optimized memory caching logic.
"""
from typing import Any, Dict, List, Optional
from rest_framework import serializers
from rest_framework.request import Request
from .models import Category, Tag, Post, Comment
from platform_seo.serializers import BaseSeoSerializer

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


class PostSeoSerializer(BaseSeoSerializer):
    """SEO fields Serializer for Blog Post."""
    
    class Meta:
        model = Post
        fields = [
            'seo_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'schema_markup',
            'og_title', 'og_type', 'og_description', 'og_url', 'og_site_name', 'og_locale', 'article_author'
        ]

    def get_canonical_url(self, obj: Post) -> str:
        """Override to provide frontend blog path."""
        return self.get_frontend_url(f"/blog/{obj.slug}/")


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
        """Return approved comments using smart prefetched checks to avoid N+1."""
        if hasattr(obj, 'approved_comments'):
            return BlogCommentSerializer(obj.approved_comments, many=True).data
        approved_comments = obj.comments.filter(is_approved=True)
        return BlogCommentSerializer(approved_comments, many=True).data