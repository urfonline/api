from django.contrib import admin
from django.contrib.admin import register

from .models import Event


@register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'associated_show')
