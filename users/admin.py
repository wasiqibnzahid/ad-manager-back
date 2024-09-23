from django.contrib import admin
from .models import NormalUser
from django.contrib.auth.admin import UserAdmin


class AdminUser(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('report_id',)}),
    )


admin.site.register(NormalUser, AdminUser)
