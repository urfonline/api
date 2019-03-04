from django.contrib import admin
from django.contrib.admin import register

from api.streams.models import StreamConfiguration

@register(StreamConfiguration)
class StreamConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'mountpoint', 'priority_online')
