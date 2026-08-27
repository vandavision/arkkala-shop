from django.urls import path
from home.api.views.home_data import HomePageDataView
from home.api.views.settings import SiteSettingView
from home.api.views.faqs import FAQListView
from home.api.views.about import AboutPageDetailView
from home.api.views.contact import ContactMessageAPIView

urlpatterns: list = [
    path('', HomePageDataView.as_view(), name='home-data'),
    path('settings/', SiteSettingView.as_view(), name='site_settings'),
    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('about/', AboutPageDetailView.as_view(), name='about-detail'),
    path('contact/', ContactMessageAPIView.as_view(), name='contact-us'),
]