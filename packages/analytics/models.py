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
        user = self.user.email.split('@')[0] or self.user.id
        return "{} ({})".format(user, self.domain)


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


class Visit(models.Model):
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
    )

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

    class Meta:
        verbose_name = _('Page Visit Count')
        verbose_name_plural = _('Page Visit Counts')


"""
# will need that later if wanna track country city etc.
def ip_location_lookup(ip, kind, lookup):
    try:
        return lookup[ip]
    except:
        g = GeoIP2()
        try:
            attr = {"country_name": g.country, "city": g.city}[kind](ip)[kind]
        except: attr = "Unknown"
        lookup[ip] = attr
        return attr
"""

