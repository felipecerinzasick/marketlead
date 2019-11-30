from django.urls import path

from .views import (
    home, add_code_to_site,
    NewCampaignView, SingleCampaignView,
    EditCampaignView, AllCampaignView,
    TrafficCounter
)

app_name = 'analytics'

urlpatterns = [
    path('', home, name='home'),
    path('campaign/', AllCampaignView.as_view(), name='all-campaign'),
    path('campaign/add-code/', add_code_to_site, name='add-code'),
    path('campaign/new/', NewCampaignView.as_view(), name='new-campaign'),
    path('campaign/view/<int:pk>/', SingleCampaignView.as_view(), name='view-campaign'),
    path('campaign/edit/<int:pk>/', EditCampaignView.as_view(), name='edit-campaign'),
    path('traffic/', TrafficCounter.as_view(), name='test_ajax')
]
