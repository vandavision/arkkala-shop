from django.urls import path, include

app_name = 'users'

urlpatterns = [
    path('', include('users.api.urls')),
]