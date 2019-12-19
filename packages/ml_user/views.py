import requests

from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView)
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import NoReverseMatch, reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .emails import EmailFromTemplate
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
    context = {
        "form": form
    }

    if request.GET.get('verify') == '1':
        context.update({
            "verify": True,
        })
    return render(
        request,
        template_name="users/login.html",
        context=context,
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
                # print("activation_link: ", activation_link)

                eft = EmailFromTemplate(
                    subject='Verify your email address',
                    to_email=user.email,
                    template_name='verify-email.html',
                    context={
                        "verification_url": activation_link
                    },
                )
                eft.send_mail()

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
        return redirect("{}?verify=1".format(reverse('login')))

    return HttpResponseForbidden("Invalid activation link")


class CustomPasswordResetView(PasswordResetView):
    title = 'Password reset'
    template_name = 'users/password/reset-form.html'
    email_template_name = 'email/password-reset.html'
    html_email_template_name = 'email/password-reset.html'
    subject_template_name = 'email/password-reset-email-subject.txt'
    success_url = reverse_lazy('user-auth:reset-password-done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    title = 'Password reset sent'
    template_name = 'users/password/reset-done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    title = 'Enter new password'
    template_name = 'users/password/reset-confirmation.html'
    success_url = reverse_lazy('user-auth:reset-password-success')


class CustomPasswordResetSuccessView(PasswordResetCompleteView):
    title = 'Password reset complete'
    template_name = 'users/password/reset-complete.html'


@method_decorator([login_required, ], name='dispatch')
class GetFbAccessToken(View):
    def get(self, request, *args, **kwargs):
        access_token = request.user.get_access_token()
        if access_token:
            return JsonResponse({
                "success": True,
                "access_token": access_token
            })
        return JsonResponse({
            "success": False,
        })
