from django.contrib import admin
from django.contrib.admin import register
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from .models import ShowApplication, TimeSlotRequest, ShowApplicationSettings


class AcceptedListFilter(admin.SimpleListFilter):
    title = 'accepted status'
    parameter_name = 'is_accepted'

    def lookups(self, request, model_admin):
        return [
            ('1', _('Accepted')),
            ('0', _('Not yet accepted')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(accepted_slot__isnull=False)
        if self.value() == '0':
            return queryset.filter(accepted_slot__isnull=True)

        return queryset


@register(ShowApplication)
class ShowApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_name', 'category',)
    list_select_related = ('owner', 'category',)
    search_fields = ('name', 'owner__name',)
    list_filter = ('category', AcceptedListFilter,)

    actions = ('make_shows',)

    readonly_fields = (
        'name',
        'cover', 'cover_width', 'cover_height',
        'banner', 'banner_width', 'banner_height',
        'first_slot_choice', 'second_slot_choice', 'third_slot_choice',
    )

    def make_shows(self, request, queryset):
        pass

    make_shows.short_description = 'Turn selected applications into shows'

@register(TimeSlotRequest)
class TimeSlotRequestAdmin(admin.ModelAdmin):
    list_display = ('day', 'hour',)

@register(ShowApplicationSettings)
class ShowApplicationSettingsAdmin(SingletonModelAdmin):
    pass
