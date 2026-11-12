import logging

from django.conf import settings
from django.http import Http404
from django.http import HttpResponsePermanentRedirect as PermanentRedirect
from django.http import HttpResponseRedirect as TemporaryRedirect
from django.urls import NoReverseMatch, reverse
from django.utils.deprecation import MiddlewareMixin
from platform_seo.helpers.enums import RedirectType
from platform_seo.models import SlugSwap

logger = logging.getLogger(__name__)


class OldSlugRedirectMiddleware(MiddlewareMixin):
    """
    Middleware to handle old slug redirection safely without redirect loops.
    """

    def process_response(self, request, response):
        if response.status_code != 404 or not getattr(request, "resolver_match", None):
            return response

        try:
            slug_mapping = getattr(settings, "SLUG_TYPE_MAPPING", {
                "product_slug": "product",
                "category_slug": "category",
                "post_slug": "post",
                "slug": "product",
            })

            current_kwargs = dict(request.resolver_match.kwargs or {})
            updated_kwargs = dict(current_kwargs)
            matched_swap = None

            for slug_name, slug_type in slug_mapping.items():
                old_slug = current_kwargs.get(slug_name)
                if old_slug:
                    swap = self._get_slug_swap(old_slug, slug_type)
                    if swap and swap.new_slug != old_slug:
                        updated_kwargs[slug_name] = swap.new_slug
                        matched_swap = swap

            if matched_swap:
                try:
                    new_url = reverse(request.resolver_match.view_name, kwargs=updated_kwargs)
                    if matched_swap.redirect_type == RedirectType.Primary:
                        return PermanentRedirect(new_url)
                    return TemporaryRedirect(new_url)
                except NoReverseMatch as e:
                    logger.error(f"NoReverseMatch: {e} for view {request.resolver_match.view_name}")
                    raise Http404("Page not found.")

        except Http404:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OldSlugRedirectMiddleware: {e}")

        return response

    def _get_slug_swap(self, old_slug: str, slug_type: str) -> SlugSwap | None:
        try:
            return SlugSwap.objects.filter(
                old_slug=old_slug, content_type__model=slug_type
            ).order_by("-id").first()
        except Exception as e:
            logger.error(f"Error retrieving new slug for {old_slug} ({slug_type}): {e}")
            return None