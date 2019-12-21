from django.contrib import admin

from .models import FbAdAccount, InsightData


@admin.register(FbAdAccount)
class AdAccountAdmin(admin.ModelAdmin):
    list_display = ['account_id', 'fb_acc', 'is_selected', ]
    raw_id_fields = ('fb_acc',)


@admin.register(InsightData)
class InsightDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'ad_id', 'created_at', ]

    def user(self, obj):
        return obj.ad_acc.fb_acc.user

    def ad_id(self, obj):
        return obj.ad_acc.ads_id or obj.ad_acc.account_id


