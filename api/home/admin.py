from django.contrib import admin
from api.home.models import HomepageBlock


@admin.register(HomepageBlock)
class HomepageBlockAdmin(admin.ModelAdmin):
    pass
