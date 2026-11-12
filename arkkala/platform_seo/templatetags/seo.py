import logging

from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from platform_seo.funcs import build_json_ld, build_robots_meta, get_meta_info

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def render_meta_tags(view_name):
    """Renders meta tags and JSON-LD for static views."""
    try:
        meta_info = get_meta_info(view_name)
    except Exception:
        return ""

    if not meta_info:
        return ""

    if isinstance(meta_info.keywords, list):
        keywords_str = ", ".join(str(k) for k in meta_info.keywords if k)
        meta_keyword_tag = format_html('<meta name="keywords" content="{}">', keywords_str)
    elif isinstance(meta_info.keywords, str):
        meta_keyword_tag = format_html('<meta name="keywords" content="{}">', meta_info.keywords)
    else:
        meta_keyword_tag = format_html('<meta name="keywords" content="">')

    meta_tags = [
        format_html("<title>{}</title>", meta_info.title),
        format_html('<meta name="description" content="{}">', meta_info.description),
        meta_keyword_tag,
        format_html(
            '<meta name="robots" content="{}">',
            build_robots_meta(meta_info.index_page, meta_info.follow_page_links),
        ),
    ]

    if meta_info.canonical_url:
        meta_tags.append(
            format_html('<link rel="canonical" href="{}" />', meta_info.canonical_url)
        )

    json_ld_script = build_json_ld(meta_info.json_ld)
    if json_ld_script:
        meta_tags.append(json_ld_script)

    return mark_safe("".join(meta_tags))


@register.simple_tag
def render_detail_meta_tags(obj):
    """Renders SEO, OpenGraph, Twitter, and JSON-LD tags for model instances."""
    if not obj:
        return ""

    meta_tags = []

    if getattr(obj, "title", None):
        meta_tags.append(format_html("<title>{}</title>", obj.title))

    # Support both 'keywords' (from MetaKeyMixin) and 'meta_keywords'
    raw_keywords = getattr(obj, "keywords", None) or getattr(obj, "meta_keywords", None)
    if raw_keywords:
        if isinstance(raw_keywords, list):
            keywords_str = ", ".join(str(k) for k in raw_keywords if k)
        else:
            keywords_str = str(raw_keywords)
        meta_tags.append(format_html('<meta name="keywords" content="{}">', keywords_str))

    if getattr(obj, "meta_description", None):
        meta_tags.append(
            format_html('<meta name="description" content="{}">', obj.meta_description)
        )

    # Use generated JSON-LD if available on the model, otherwise fallback to json_ld field
    schema_data = (
        obj.generate_json_ld()
        if hasattr(obj, "generate_json_ld")
        else getattr(obj, "json_ld", None)
    )
    if schema_data:
        json_ld_script = build_json_ld(schema_data)
        if json_ld_script:
            meta_tags.append(json_ld_script)

    if getattr(obj, "og_title", None):
        meta_tags.append(
            format_html('<meta property="og:title" content="{}">', obj.og_title)
        )

    if getattr(obj, "og_type", None):
        meta_tags.append(
            format_html('<meta property="og:type" content="{}">', obj.og_type)
        )

    og_image = getattr(obj, "og_image", None)
    if og_image:
        img_url = og_image.url if hasattr(og_image, "url") else str(og_image)
        if img_url:
            meta_tags.append(
                format_html('<meta property="og:image" content="{}">', img_url)
            )

    if getattr(obj, "og_description", None):
        meta_tags.append(
            format_html('<meta property="og:description" content="{}">', obj.og_description)
        )

    if getattr(obj, "twitter_card", None):
        meta_tags.append(
            format_html('<meta name="twitter:card" content="{}">', obj.twitter_card)
        )

    if getattr(obj, "twitter_site", None):
        meta_tags.append(
            format_html('<meta name="twitter:site" content="{}">', obj.twitter_site)
        )

    if getattr(obj, "twitter_creator", None):
        meta_tags.append(
            format_html('<meta name="twitter:creator" content="{}">', obj.twitter_creator)
        )

    twitter_image = getattr(obj, "twitter_image", None)
    if twitter_image:
        img_url = twitter_image.url if hasattr(twitter_image, "url") else str(twitter_image)
        if img_url:
            meta_tags.append(
                format_html('<meta name="twitter:image" content="{}">', img_url)
            )

    frontend_url = getattr(settings, "FRONTEND_URL", "https://arkkala.com").rstrip("/")
    try:
        if hasattr(obj, "get_absolute_url"):
            canonical_url = f"{frontend_url}{obj.get_absolute_url()}"
            meta_tags.append(
                format_html('<link rel="canonical" href="{}" />', canonical_url)
            )
    except Exception as e:
        logger.debug(e, exc_info=True)

    return mark_safe("".join(meta_tags))