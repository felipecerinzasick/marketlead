import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
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
        time_now = datetime.datetime.now(tz=timezone.utc)
        from_date = time_now - datetime.timedelta(days=day)
        return self.sitevisit_set.filter(created__range=[from_date, time_now]).count()


class Page(models.Model):
    host = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    keyword = models.CharField(max_length=50, help_text="Must be unique in same domain")

    class Meta:
        unique_together = ('host', 'keyword',)

    def __str__(self):
        return self.name

    def get_visit_count_by_day(self, day=7):
        time_now = datetime.datetime.now(tz=timezone.utc)
        from_date = time_now - datetime.timedelta(days=day)
        return self.pagevisit_set.filter(created__range=[from_date, time_now]).count()

    def get_bounce_rate_by_day(self, day=7):
        next_page = None
        for pg in Page.objects.filter(host=self.host).order_by('-id'):
            if pg == self:
                break
            next_page = pg
        if next_page is None:
            return "-"  # no bounce rate for last page
        next_page_visit = next_page.pagevisit_set.count()
        this_page_visit = self.pagevisit_set.count()

        if this_page_visit < next_page_visit:
            return '100%'
        if this_page_visit == 0:
            return '0%'
        ptg = "{0:.2f}".format(100 * next_page_visit/this_page_visit)
        if ptg[-2:] == '00':    # remove 00 after point (if whole number)
            ptg = ptg[:-3]
        return "{}%".format(ptg)


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
    updated = models.DateTimeField(
        _("Last Visited"),
        auto_now=True,
    )


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



