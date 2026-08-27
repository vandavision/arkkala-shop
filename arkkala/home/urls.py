from django.urls import path, include

urlpatterns: list = [
    path('', include('home.api.urls')),
]