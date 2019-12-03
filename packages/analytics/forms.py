import secrets

from django import forms

from .models import Client, Page


class ClientForm(forms.ModelForm):
    track_id = forms.CharField(required=False)

    class Meta:
        model = Client
        exclude = ('is_verified', )

    def clean_track_id(self):
        return secrets.token_urlsafe(25)


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['host'].required = False

