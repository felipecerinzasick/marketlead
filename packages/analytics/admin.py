from django.contrib import admin

from .models import Client, Page, PageVisit, SiteVisit


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["domain", "user", "url", "is_verified", "track_id",]
    list_filter = ['is_verified',]
    search_fields = ['domain', 'url']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["name", "keyword", "host"]
    list_filter = ['host',]
    search_fields = ['name', 'host', 'keyword']


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ["page", "host", "ip_addr", "created", "updated",]
    date_hierarchy = 'created'
    search_fields = ['page',]

    def host(self, obj):
        return obj.page.host.domain


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ["site", "ip_addr", "created", "updated",]
    date_hierarchy = 'created'
    search_fields = ['site',]




