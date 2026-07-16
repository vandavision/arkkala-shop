from django.urls import path
from .views import HomePageDataView, SiteSettingView, FAQListView, AboutPageDetailView, ContactMessageAPIView

urlpatterns = [
    path('', HomePageDataView.as_view(), name='home-data'),
    path('settings/', SiteSettingView.as_view(), name='site_settings'),
    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('about/', AboutPageDetailView.as_view(), name='about-detail'),
    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('about/', AboutPageDetailView.as_view(), name='about-detail'),
    path('contact/', ContactMessageAPIView.as_view(), name='contact-us'),
]