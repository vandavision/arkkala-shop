import logging

from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.urls import Resolver404, resolve
from django.utils.deprecation import MiddlewareMixin

from platform_seo.helpers.enums import RedirectType
from platform_seo.models import URLRedirect

logger = logging.getLogger(__name__)


class URLRedirectMiddleware(MiddlewareMixin):
    """
    Middleware to handle URL redirection based on database entries, respecting 301 vs 302.
    """

    def process_response(self, request, response):
        if response.status_code == 404:
            url_mapping = self.get_redirect_mapping(request.path)
            if url_mapping and url_mapping.new_url != request.path:
                if url_mapping.redirect_type == RedirectType.Primary:
                    return HttpResponsePermanentRedirect(url_mapping.new_url)
                return HttpResponseRedirect(url_mapping.new_url)

        return response

    def url_exists_in_urlpatterns(self, url: str) -> bool:
        try:
            resolve(url)
            return True
        except Resolver404:
            return False

    def get_redirect_mapping(self, old_url: str) -> URLRedirect | None:
        try:
            return URLRedirect.objects.filter(old_url=old_url).first()
        except Exception:
            return None