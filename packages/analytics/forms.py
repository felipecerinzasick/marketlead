import secrets

from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    unique_id = forms.CharField(required=False)

    class Meta:
        model = Client
        exclude = ('is_verified', )

    def clean_unique_id(self):
        return secrets.token_urlsafe(25)
