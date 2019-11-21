from django.urls import path

from .views import home

app_name = 'analytics'

urlpatterns = [
    path('', home, name='home'),
]