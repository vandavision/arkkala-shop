"""
Blog Models including Category, Tag, Post, and Comments.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin, BlogDetailJsonLdMixin
from typing import Dict, Any, List
from django.conf import settings
User = get_user_model()


class Category(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """Blog Category Model."""
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('دسته بندی مقالات')
        verbose_name_plural = _('دسته بندی های مقالات')


class Tag(UUIDBaseModel, TimeStampMixin, TitleSlugMixin):
    """Blog Tag Model."""
    class Meta:
        verbose_name = _('برچسب')
        verbose_name_plural = _('برچسب ها')


class Post(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin, BlogDetailJsonLdMixin):
    """Main Blog Post Model."""
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name=_('نویسنده'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name=_('دسته بندی'))
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name=_('برچسب ها'))
    
    image = models.ImageField(upload_to='blog/posts/', null=True, blank=True, verbose_name=_('تصویر کاور'))
    short_description = models.TextField(verbose_name=_('توضیح کوتاه (چکیده)'))
    body = models.TextField(verbose_name=_('متن کامل مقاله'))
    
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد بازدید'))
    read_time = models.PositiveIntegerField(default=5, verbose_name=_('زمان مطالعه (دقیقه)'))
    
    is_published = models.BooleanField(default=True, verbose_name=_('منتشر شده'))

    class Meta:
        verbose_name = _('مقاله')
        verbose_name_plural = _('مقالات')
        ordering = ['-created_at']


    def generate_json_ld(self) -> Dict[str, Any]:
        """
        Generates comprehensive JSON-LD including Article Schema and BreadcrumbList.
        
        Returns:
            Dict[str, Any]: A dictionary containing the structured JSON-LD data.
        """
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        post_url: str = f"{frontend_domain}/blog/{self.slug}/"
        author_name: str = self.article_author or (self.author.get_full_name() if self.author else getattr(settings, 'SITE_NAME', 'ارک کالا'))

        json_ld: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "headline": self.title,
                    "image": [self.image.url if self.image else ""],
                    "datePublished": self.created_at.isoformat(),
                    "dateModified": self.modified_at.isoformat(),
                    "author": {
                        "@type": "Person",
                        "name": author_name
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": getattr(settings, 'SITE_NAME', 'ارک کالا'),
                        "logo": {
                            "@type": "ImageObject",
                            "url": f"{frontend_domain}/assets/image/logo.png"
                        }
                    },
                    "description": self.meta_description or self.short_description or self.title,
                    "mainEntityOfPage": {
                        "@type": "WebPage",
                        "@id": post_url
                    }
                }
            ]
        }

        if getattr(self, 'category', None):
            breadcrumbs: List[Dict[str, Any]] = [
                {"@type": "ListItem", "position": 1, "name": "خانه", "item": f"{frontend_domain}/"},
                {"@type": "ListItem", "position": 2, "name": "مجله", "item": f"{frontend_domain}/blog/"},
                {"@type": "ListItem", "position": 3, "name": self.category.title, "item": f"{frontend_domain}/blog?category__slug={self.category.slug}"},
                {"@type": "ListItem", "position": 4, "name": self.title, "item": post_url}
            ]
            json_ld["@graph"].append({
                "@type": "BreadcrumbList",
                "itemListElement": breadcrumbs
            })

        return json_ld


class Comment(UUIDBaseModel, TimeStampMixin):
    """Blog Post Comments."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('مقاله'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_comments', verbose_name=_('کاربر'))
    body = models.TextField(verbose_name=_('متن نظر'))
    is_approved = models.BooleanField(default=False, verbose_name=_('تایید شده'))

    class Meta:
        verbose_name = _('نظر مقاله')
        verbose_name_plural = _('نظرات مقالات')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"نظر روی {self.post.title}"