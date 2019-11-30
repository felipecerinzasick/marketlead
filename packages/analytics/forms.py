import secrets
from urllib.parse import urlparse

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

    def clean(self):
        # check client host and page host before saving
        cleaned_data = self.cleaned_data
        client = cleaned_data.get('host', '')
        page_url = cleaned_data.get('url', '')

        if client or page_url:
            client_url_parsed = urlparse(client.url)
            page_url_parsed = urlparse(page_url)
            if page_url_parsed.hostname != client_url_parsed.hostname:
                self.add_error('url', "Page domain is not matched with client's domain")

        return self.cleaned_data
