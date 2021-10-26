from django.contrib import admin
from django.contrib.admin import register

from api.streams.models import StreamConfiguration

@register(StreamConfiguration)
class StreamConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'proxy_url', 'priority_online')
