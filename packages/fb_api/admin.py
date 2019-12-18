from django.contrib import admin

from .models import FbAdAccount


@admin.register(FbAdAccount)
class AdAccountAdmin(admin.ModelAdmin):
    list_display = ['ads_id', 'fb_acc', 'account_id']
    raw_id_fields = ('fb_acc',)

