from django.contrib import admin
from .models import NormalUserProfile


class NormalUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'report_id')


admin.site.register(NormalUserProfile, NormalUserProfileAdmin)
