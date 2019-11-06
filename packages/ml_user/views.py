from django.contrib.auth import (
    authenticate,
    login as django_login,
    views as django_auth_views
)
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import NoReverseMatch

from .forms import EmailLoginForm


def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            if request.GET.get('next'):
                try:
                    return redirect(request.GET.get('next'))
                except NoReverseMatch as err:
                    raise Http404(err)
            return redirect("/admin/")
        else:
            redirect_field_name = "next"
            return django_auth_views.LoginView.as_view(
                template_name="users/login.html",
                redirect_field_name=redirect_field_name,
                authentication_form=EmailLoginForm,
                form_class=EmailLoginForm
            )(request)
