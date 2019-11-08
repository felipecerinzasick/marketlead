from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    password2 = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        pswd_1 = cleaned_data.get('password1')
        if pswd_1:
            self.cleaned_data['password2'] = pswd_1
        return cleaned_data


class EmailLoginForm(AuthenticationForm):
    class Meta(UserCreationForm.Meta):
        model = User
