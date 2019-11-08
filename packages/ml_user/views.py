from django.contrib.auth import (
    authenticate,
    login as django_login,
    views as django_auth_views,
    logout as django_logout,
)
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import NoReverseMatch

from .forms import EmailLoginForm, RegistrationForm


def login(request):
    # if already logged in
    if request.user.is_authenticated:
        return redirect("/")    # todo: set logged in url

    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, email=email, password=password)
    if user is not None:
        django_login(request, user)
        if request.GET.get('next'):
            try:
                return redirect(request.GET.get('next'))
            except NoReverseMatch as err:
                raise Http404(err)
        return redirect("/")    # todo: set logged in url
    else:
        redirect_field_name = "next"
        return django_auth_views.LoginView.as_view(
            template_name="users/login.html",
            redirect_field_name=redirect_field_name,
            authentication_form=EmailLoginForm,
            form_class=EmailLoginForm
        )(request)


def sign_up(request):
    # if already logged in
    if request.user.is_authenticated:
        return redirect('/')    # todo: set logged in url

    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password1)
            print(user)

            django_login(request, user)
            return redirect('/')    # todo: set logged in url

    return render(
        request,
        template_name='users/register.html',
        context={
            'form': form
        }
    )


def logout(request):
    django_logout(request)
    return redirect('/')    # todo: set logged in url

