"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from ml_user.views import (
    login as login_view,
    sign_up as signup_view,
    logout as logout_view,
)


urlpatterns = [
    path('', include('analytics.urls', namespace='analytics')),
    path('login/', login_view, name='login'),
    path('sign-up/', signup_view, name='sign-up'),
    path('logout/', logout_view, name='logout'),
    path('user/', include('ml_user.urls', namespace='user-auth')),
    path('admin/', admin.site.urls),
]
