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
    pass


@register(ShowSlot)
class ShowSlotAdmin(admin.ModelAdmin):
    pass


@register(ScheduleSlate)
class ScheduleSlateAdmin(admin.ModelAdmin):
    pass


@register(ShowSeries)
class ShowSeriesAdmin(admin.ModelAdmin):
    pass


@register(ShowEpisode)
class ShowEpisodeAdmin(admin.ModelAdmin):
    pass


@register(EpisodeCredit)
class EpisodeCreditAdmin(admin.ModelAdmin):
    pass


@register(ShowsConfiguration)
class ShowsConfigurationAdmin(SingletonModelAdmin):
    pass


