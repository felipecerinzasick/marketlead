from django.urls import path

from .views import (verify_signup, verification_msg,
                    CustomPasswordResetView, CustomPasswordResetDoneView,
                    CustomPasswordResetConfirmView, CustomPasswordResetSuccessView)

app_name = 'user-auth'

urlpatterns = [
    path('verification-email-send/', verification_msg, name='verification'),
    path('tokenized-verify/', verify_signup, name='verify'),
    path('reset-password/', CustomPasswordResetView.as_view(), name='reset-password'),
    path('reset-password/done/', CustomPasswordResetDoneView.as_view(), name='reset-password-done'),
    path('reset-password/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='reset-password-confirm'),
    path('reset-password/success/', CustomPasswordResetSuccessView.as_view(), name='reset-password-success'),
]
