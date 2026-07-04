from django.urls import path
from .views import HomePageDataView

urlpatterns = [
    path('', HomePageDataView.as_view(), name='home-data'),
]