from django.contrib import admin
from django.contrib.admin import register
from solo.admin import SingletonModelAdmin

from api.shows.models import Show, ShowSlot, ScheduleSlate, ShowSeries, ShowEpisode, EpisodeCredit,\
    ShowsConfiguration, ShowCategory


@register(ShowCategory)
class ShowCategoryAdmin(admin.ModelAdmin):
    pass


@register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ['name', ]


@register(ShowSlot)
class ShowSlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'week', 'start_time', 'end_time',)
    search_fields = ('show__name',)
    list_filter = ('day', 'week',)

@register(ScheduleSlate)
class ScheduleSlateAdmin(admin.ModelAdmin):
    pass


@register(ShowSeries)
class ShowSeriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'show', 'type')


@register(ShowEpisode)
class ShowEpisodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'show', 'series', 'published_at')


@register(EpisodeCredit)
class EpisodeCreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'episode', 'role')


@register(ShowsConfiguration)
class ShowsConfigurationAdmin(SingletonModelAdmin):
    pass


