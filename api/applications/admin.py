from django.contrib import admin
from django.contrib.admin import register
from django.forms import Widget, ModelForm
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
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
            return queryset.filter(assigned_slot__isnull=False)
        if self.value() == '0':
            return queryset.filter(assigned_slot__isnull=True)

        return queryset

class TimeSlotWidget(Widget):
    def render(self, name, value, attrs=None):
        if value is None:
            return ""

        slot = TimeSlotRequest.objects.get(pk=value)
        context = {
            'slot_request': slot,
            'taken': slot.is_taken(),
            'slot_name': name,
        }

        # if slot.is_taken():
        #     context['taken_by_self'] = slot.accepted_application ==

        return mark_safe(render_to_string('admin/time_slot_widget.html', context))

class ShowApplicationForm(ModelForm):
    class Meta:
        model = ShowApplication
        fields = '__all__'
        widgets = {
            'first_slot_choice': TimeSlotWidget,
            'second_slot_choice': TimeSlotWidget,
            'third_slot_choice': TimeSlotWidget,
        }

@register(ShowApplication)
class ShowApplicationAdmin(admin.ModelAdmin):
    form = ShowApplicationForm
    list_display = ('name', 'user_name', 'category',)
    list_select_related = ('owner', 'category',)
    search_fields = ('name', 'owner__name',)
    list_filter = ('category', AcceptedListFilter,)

    actions = ('make_shows',)

    readonly_fields = (
        'name',
        'cover', 'cover_width', 'cover_height',
        'banner', 'banner_width', 'banner_height',
    )

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'short_description', 'long_description', 'brand_color', 'emoji_description', 'category')
        }),
        ('Slot Choices', {
            'fields': ('first_slot_choice', 'second_slot_choice', 'third_slot_choice', 'assigned_slot')
        }),
        ('Miscellaneous', {
            'fields': ('contact_email', 'cover', 'banner',
                       'social_facebook_url', 'social_twitter_handle', 'social_mixcloud_handle', 'social_youtube_url',
                       'social_snapchat_handle', 'social_instagram_handle', 'social_soundcloud_handle',)
        }),
    )

    def make_shows(self, request, queryset):
        pass

    make_shows.short_description = 'Turn selected applications into shows'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name.endswith('_slot_choice'):
            return self.formfield_for_foreignkey(db_field, request, **kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def response_change(self, request, obj):
        choice = None

        if 'assign_first_slot_choice' in request.POST:
            choice = int(request.POST['first_slot_choice'])
        elif 'assign_second_slot_choice' in request.POST:
            choice = int(request.POST['second_slot_choice'])
        elif 'assign_third_slot_choice' in request.POST:
            choice = int(request.POST['third_slot_choice'])

        if choice is not None:
            obj.assigned_slot = TimeSlotRequest.objects.get(pk=choice)
            obj.save(update_fields=['assigned_slot'])
            request.POST['_continue'] = ""

        return super().response_change(request, obj)

@register(TimeSlotRequest)
class TimeSlotRequestAdmin(admin.ModelAdmin):
    list_display = ('day', 'hour',)

@register(ShowApplicationSettings)
class ShowApplicationSettingsAdmin(SingletonModelAdmin):
    pass
