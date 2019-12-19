from django.contrib import admin

from .models import FbAdAccount


@admin.register(FbAdAccount)
class AdAccountAdmin(admin.ModelAdmin):
    list_display = ['account_id', 'fb_acc', 'is_selected', ]
    raw_id_fields = ('fb_acc',)

