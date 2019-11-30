from django.contrib import admin

from .models import Client, Page, Visit


admin.site.register(Client)
admin.site.register(Page)
admin.site.register(Visit)