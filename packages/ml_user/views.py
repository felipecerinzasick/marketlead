import requests

from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
# from django.core.mail import EmailMessage
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, reverse
from django.urls import NoReverseMatch
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt

from .forms import EmailLoginForm, RegistrationForm
from .models import User
from .tokens import account_activation_token
from .utils import get_full_url, allowed_post_only


def login(request):
    # if already logged in
    if request.user.is_authenticated:
        return redirect("/")    # todo: set logged in url

    form = EmailLoginForm()
    if request.POST:
        form = EmailLoginForm(request.POST)
        if form.is_valid():
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
            print(form.errors)
    return render(
        request,
        template_name="users/login.html",
        context={
            "form": form
        }
    )


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
            if user is not None:
                # Send an email to the user with the token:
                verfiy_url = get_full_url(request, rel_url=reverse('user-auth:verify'))
                uid = urlsafe_base64_encode(force_bytes(user.id))
                token = account_activation_token.make_token(user)
                activation_link = "{0}?uid={1}&token={2}".format(verfiy_url, uid, token)
                print("activation_link: ", activation_link)
                # message = "Hello {0},\n {1}".format(user.email, activation_link)
                # mail_subject = 'Activate your account.'
                # email_msg = EmailMessage(mail_subject, message, to=[email])
                # email_msg.send()

                _url = get_full_url(request, rel_url=reverse('user-auth:verification'))
                r = requests.post(url=_url, data={"id": 55})
                return HttpResponse(
                    content=r.content,
                    status=r.status_code,
                    content_type=r.headers['Content-Type']
                )
        # else:
        #     print(form.errors)
    return render(
        request,
        template_name='users/register.html',
        context={
            'form': form
        }
    )


def logout(request):
    django_logout(request)
    return redirect('login')    # todo: set logged in url


@csrf_exempt
@allowed_post_only
def verification_msg(request):
    # if already logged in
    if request.user.is_authenticated:
        return redirect('/')    # todo: set logged in url

    return render(request, 'users/verification-msg.html')


def verify_signup(request):
    # if already logged in
    if request.user.is_authenticated:
        return redirect('/')    # todo: set logged in url

    try:
        uidb64 = request.GET.get('uid', None)
        token = request.GET.get('token', None)
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # activate user and login:
        user.is_active = True
        user.is_verified = True
        user.save()
        django_login(request, user)
        return redirect('/')

    return HttpResponseForbidden("Invalid activation link")
