from typing import Any, Dict, List
from rest_framework import serializers
from platform_seo.serializers import BaseSeoSerializer
from blog.models.post import Post
from .category import BlogCategorySerializer
from .tag import TagSerializer
from .comment import BlogCommentSerializer

class PostSeoSerializer(BaseSeoSerializer):
    class Meta:
        model = Post
        fields = [
            'seo_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'schema_markup',
            'og_title', 'og_type', 'og_description', 'og_url', 'og_site_name', 'og_locale', 'article_author',
            'twitter_card', 'twitter_creator', 'twitter_site'
        ]

    def get_canonical_url(self, obj: Post) -> str:
        return self.get_frontend_url(f"/blog/{obj.slug}/")

class PostListSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Post
        fields = [
            'uuid', 'title', 'slug', 'category', 'author_name', 'image', 'image_alt', 
            'short_description', 'view_count', 'read_time', 'created_at'
        ]

class PostDetailSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    comments = serializers.SerializerMethodField()
    seo = PostSeoSerializer(source='*', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'uuid', 'title', 'slug', 'category', 'tags', 'author_name', 'image', 'image_alt',
            'short_description', 'body', 'key_takeaways', 'expert_reviewer', 'faq_data', 'citations',
            'view_count', 'read_time', 'comments', 'seo', 'created_at'
        ]

    def get_comments(self, obj: Post) -> List[Dict[str, Any]]:
        if hasattr(obj, 'approved_comments'):
            return BlogCommentSerializer(obj.approved_comments, many=True).data
        return BlogCommentSerializer(obj.comments.filter(is_approved=True), many=True).data