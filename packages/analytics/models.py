import datetime

from urllib.parse import urlparse

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


User = get_user_model()

URL_HELP_TEXT = "URL must be with or without scheme (http/https)"


class Client(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    domain = models.CharField(
        _("Site Name"),
        max_length=255,
    )
    url = models.URLField(
        _("Site URL"),
        help_text=URL_HELP_TEXT
    )
    is_verified = models.BooleanField(default=False)

    track_id = models.CharField(
        _("Track ID"),
        max_length=50,
        unique=True,
    )

    class Meta:
        unique_together = ('user', 'url',)

    def __str__(self):
        return self.domain

    def get_visit_count_by_day(self, day=7):
        time_now = datetime.datetime.now()
        from_date = time_now - datetime.timedelta(days=day)
        return self.sitevisit_set.filter(created__range=[from_date, time_now]).count()


class Page(models.Model):
    host = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    url = models.URLField(help_text=URL_HELP_TEXT)

    class Meta:
        unique_together = ('host', 'url',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # check client host and page host before saving
        if getattr(self, 'url') and getattr(self, 'host'):
            page_url_parsed = urlparse(self.url)
            client_url_parsed = urlparse(self.host.url)
            if page_url_parsed.hostname != client_url_parsed.hostname:
                raise KeyError("Page domain is not matched with client's domain")
        super(Page, self).save(*args, **kwargs)

    def get_visit_count_by_day(self, day=7):
        time_now = datetime.datetime.now()
        from_date = time_now - datetime.timedelta(days=day)
        return self.pagevisit_set.filter(created__range=[from_date, time_now]).count()

    def get_bounce_rate_by_day(self, day=7):
        if self.host.get_visit_count_by_day(day) == 0:
            return '0%'
        return "{}%".format(
            (self.get_visit_count_by_day(day) / self.host.get_visit_count_by_day(day))*100
        )


class Visit(models.Model):
    ip_addr = models.CharField(
        _("IP Address"),
        max_length=64,
        blank=True, null=True,
    )
    created = models.DateTimeField(
        _("First Visited"),
        auto_now_add=True,
    )
    # updated = models.DateTimeField(
    #     _("Last Visited"),
    #     auto_now=True,
    # )


class PageVisit(Visit):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('Page Visit Count')
        verbose_name_plural = _('Page Visit Counts')


class SiteVisit(Visit):
    site = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('Website Visit Count')
        verbose_name_plural = _('Website Visit Counts')



