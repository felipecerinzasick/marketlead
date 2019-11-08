from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name',)
    fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('email',)

