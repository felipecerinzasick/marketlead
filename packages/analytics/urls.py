from django.urls import path

from .views import home, add_code_to_site

app_name = 'analytics'

urlpatterns = [
    path('', home, name='home'),
    path('campaign/add-code/', add_code_to_site, name='add-code'),
]