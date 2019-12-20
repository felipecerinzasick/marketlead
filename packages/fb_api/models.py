from django.db import models
from django.utils.translation import ugettext_lazy as _
from social_django.models import UserSocialAuth

from fb_api.api_caller import ApiParser


class FbAdAccount(models.Model):
    fb_acc = models.ForeignKey(
        UserSocialAuth,
        on_delete=models.CASCADE,
        verbose_name=_("Social Auth Model"),
    )
    ads_id = models.CharField(_("Ads ID"), max_length=50)
    account_id = models.CharField(_("Account ID"), max_length=30)
    is_selected = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Ad Account")
        verbose_name_plural = _("Ad Accounts")

    def __str__(self):
        return "{}({})".format(self.fb_acc.user.username or self.fb_acc.user.email, self.account_id)

    def get_user(self):
        return self.fb_acc.user

    def get_insight_data(self, from_time, to_time):
        access_token = self.fb_acc.extra_data.get('access_token', '')
        fbap = ApiParser(token=access_token)
        return fbap.get_ads_insight(self.ads_id, from_time, to_time)


