import json
import secrets
import string

from django.db.models import Q
from django.urls import URLPattern, URLResolver
from django.utils.safestring import mark_safe
from django.views.generic import DetailView

from platform_seo.helpers.enums import SearchEngineRules


def get_meta_info(view_name: str):
    """
    Retrieve MetaInformation instance based on the raw or processed view_name.

    Returns:
        MetaInformation: An instance of MetaInformation or None if not found.
    """
    if not view_name:
        return None

    from platform_seo.models import MetaInformation

    # Check if ':' exists in the view_name and process accordingly
    if ":" in view_name:
        processed_view_name = view_name.split(":", 1)[1].replace("-", " ").title()
    else:
        processed_view_name = view_name.replace("-", " ").title()

    return (
        MetaInformation.objects.filter(
            Q(view_name__iexact=view_name)
            | Q(view_name__istartswith=processed_view_name)
        ).first()
    )


def build_robots_meta(index_page: bool, follow_page_links: bool) -> str:
    """Construct content value for the robots meta tag."""
    return ", ".join(
        [
            SearchEngineRules.INDEX if index_page else SearchEngineRules.NOINDEX,
            (
                SearchEngineRules.FOLLOW
                if follow_page_links
                else SearchEngineRules.NOFOLLOW
            ),
        ]
    )


def build_json_ld(json_ld) -> str:
    """
    Return a script tag with valid, XSS-safe JSON-LD data if present.
    Preserves valid JSON quotes while escaping closing script tags.
    """
    if not json_ld:
        return ""

    if isinstance(json_ld, str):
        try:
            json_ld = json.loads(json_ld)
        except ValueError:
            return ""

    json_ld_data = json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/")
    return mark_safe(f'<script type="application/ld+json">{json_ld_data}</script>')


def generate_short_code(length: int = 6) -> str:
    """Generate a cryptographically secure random string of the specified length."""
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def collect_view_names(patterns, app_names):
    view_names = []
    for pattern in patterns:
        if isinstance(pattern, URLPattern):
            view_func = pattern.callback
            view_module = view_func.__module__
            # Exclude admin views
            if "admin" in view_module:
                continue
            if hasattr(view_func, "view_class"):
                # Check if the view is a DetailView or a subclass thereof
                if issubclass(view_func.view_class, DetailView):
                    continue
            if any(app_name in view_module for app_name in app_names):
                if pattern.name:
                    view_name = (
                        f'{pattern.name.replace("-", " ").title()} | {pattern.lookup_str}'
                    )
                    view_names.append(view_name)
        elif isinstance(pattern, URLResolver):
            view_names.extend(collect_view_names(pattern.url_patterns, app_names))
    return view_names