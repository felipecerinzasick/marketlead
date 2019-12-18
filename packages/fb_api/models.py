from django.db import models
from django.utils.translation import ugettext_lazy as _
from social_django.models import UserSocialAuth


class FbAdAccount(models.Model):
    fb_acc = models.ForeignKey(
        UserSocialAuth,
        on_delete=models.CASCADE,
        verbose_name=_("Social Auth Model"),
    )
    ads_id = models.CharField(_("Ads ID"), max_length=50)
    account_id = models.CharField(_("Account ID"), max_length=30)

    class Meta:
        verbose_name = _("Ad Account")
        verbose_name_plural = _("Ad Accounts")

    def __str__(self):
        return "{}({})".format(self.fb_acc.user.username or self.fb_acc.user.email, self.account_id)

    def get_user(self):
        return self.fb_acc.user


