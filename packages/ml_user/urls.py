from django.urls import path

from .views import verify_signup, verification_msg

app_name = 'user-auth'

urlpatterns = [
    path('verification-email-send/', verification_msg, name='verification'),
    path('tokenized-verify/', verify_signup, name='verify'),
]