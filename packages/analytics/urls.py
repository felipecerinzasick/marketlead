from django.urls import path

from .views import (
    home, add_code_to_site,
    NewCampaignView, SingleCampaignView,
    EditCampaignView, AllCampaignView,
    NewCampaignPageView, NewCampaignPageByClientView,
    SingleCampaignPageView, SingleCampaignAllPagesView,
    EditCampaignPageView, AllCampaignPageView,
    TrafficCounter
)

app_name = 'analytics'

urlpatterns = [
    path('', home, name='home'),
    path('campaign/add-code/', add_code_to_site, name='add-code'),

    path('campaign/all/', AllCampaignView.as_view(), name='all-campaign'),
    path('campaign/new/', NewCampaignView.as_view(), name='new-campaign'),
    path('campaign/view/<int:pk>/', SingleCampaignView.as_view(), name='view-campaign'),
    path('campaign/view/<int:pk>/pages/', SingleCampaignAllPagesView.as_view(), name='view-campaign-all-pages'),
    path('campaign/edit/<int:pk>/', EditCampaignView.as_view(), name='edit-campaign'),

    path('campaign/page/all/', AllCampaignPageView.as_view(), name='all-campaign-page'),
    path('campaign/page/new/', NewCampaignPageView.as_view(), name='new-campaign-page'),
    path('campaign/page/new/<pk>/', NewCampaignPageByClientView.as_view(), name='new-campaign-page-by-campaign'),
    path('campaign/page/view/<int:pk>/', SingleCampaignPageView.as_view(), name='view-campaign-page'),
    path('campaign/page/edit/<int:pk>/', EditCampaignPageView.as_view(), name='edit-campaign-page'),
    path('traffic/', TrafficCounter.as_view(), name='test_ajax')
]
