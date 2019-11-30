from django.contrib import admin

from .models import Client, Page, PageVisit, SiteVisit


admin.site.register(Client)
admin.site.register(Page)
admin.site.register(PageVisit)
admin.site.register(SiteVisit)
