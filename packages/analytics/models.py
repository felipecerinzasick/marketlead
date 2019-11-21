from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


class Client(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    domain = models.CharField(_("Site Name"), max_length=255,)
    url = models.URLField(_("Site URL"), help_text="Website's root url without scheme (http/https)")
    is_verified = models.BooleanField(default=False)

    unique_id = models.UUIDField(editable=False)

    def __str__(self):
        user = self.user.email.split('@')[0] or self.user.id
        return "{} ({})".format(user, self.domain)


class Visit(models.Model):
    client = models.ForeignKey(
        Client,
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

