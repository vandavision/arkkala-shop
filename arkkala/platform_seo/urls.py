"""
URLs for Platform SEO App.
"""
from django.urls import path

from .views.robot import RobotsTxtView
from .views.api import StaticPageSeoAPIView

urlpatterns = [
    # path("robots.txt", RobotsTxtView.as_view(), name="robots_txt"),
    path("api/static-seo/", StaticPageSeoAPIView.as_view(), name="static_seo_api"),
]