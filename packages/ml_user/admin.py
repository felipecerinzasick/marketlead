from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'is_verified', 'is_staff')
    fields = ('email', 'first_name', 'last_name', 'is_verified')
    readonly_fields = ('email',)

