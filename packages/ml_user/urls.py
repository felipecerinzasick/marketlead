from django.urls import path

from .views import verify_signup, verification_msg


urlpatterns = [
    path('verification-email-send/', verification_msg, name='verification'),
    path('verify-user/', verify_signup, name='verify'),
]