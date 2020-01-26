from datetime import time, timedelta, datetime, date

from django.contrib import admin, messages
from django.contrib.admin import register
from django.forms import Widget, ModelForm
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from api.shows.models import ScheduleSlate, ShowSlot, Show
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

class HasShowListFilter(admin.SimpleListFilter):
    title = 'show presence'
    parameter_name = 'has_show'

    def lookups(self, request, model_admin):
        return [
            ('1', _('Show attached')),
            ('0', _('Show not yet attached')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(connected_show__isnull=False)
        elif self.value() == '0':
            return queryset.filter(connected_show__isnull=True)

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

        help_texts = {
            'link_to_connected_show': 'When this slot has been turned into a show, it will be linked here',
        }

@register(ShowApplication)
class ShowApplicationAdmin(admin.ModelAdmin):
    form = ShowApplicationForm
    list_display = ('name', 'created_at', 'host_name', 'category',)
    list_select_related = ('owner', 'category',)
    search_fields = ('name', 'host_name', 'producer_name',)
    list_filter = ('category', AcceptedListFilter, HasShowListFilter,)

    actions = ('make_shows',)

    readonly_fields = (
        'name', 'host_name', 'contact_email', 'contact_phone',
        'cover', 'cover_width', 'cover_height',
        'banner', 'banner_width', 'banner_height',
        'created_at', 'link_to_connected_show'
    )

    fieldsets = (
        ('Applicant Info', {
            'fields': ('host_name', 'producer_name', 'contact_email', 'contact_phone', 'created_at', 'new_show')
        }),
        ('Basic Info', {
            'fields': ('name', 'short_description', 'long_description', 'brand_color', 'emoji_description', 'category')
        }),
        ('Slot Choices', {
            'fields': ('biweekly', 'first_slot_choice', 'second_slot_choice', 'third_slot_choice', 'assigned_slot')
        }),
        ('Miscellaneous', {
            'fields': ('cover', 'banner',
                       'social_facebook_url', 'social_twitter_handle', 'social_mixcloud_handle', 'social_youtube_url',
                       'social_snapchat_handle', 'social_instagram_handle', 'social_soundcloud_handle',
                       'link_to_connected_show')
        }),
    )

    def link_to_connected_show(self, obj):
        if not obj.connected_show:
            return self.admin_site.empty_value_display

        link = reverse('admin:shows_show_change', args=[obj.connected_show.id])

        return format_html('<a href="{}">{}</a>', link, obj.connected_show.name)

    link_to_connected_show.short_description = 'Connected show'

    def make_shows(self, request, queryset):
        if request.POST.get("post"):
            # Do the conversion!
            self.create_shows_in(request, queryset)
            return None

        slates = ScheduleSlate.objects.all()

        ctx = dict(
            self.admin_site.each_context(request),
            slates=slates,
            opts=self.model._meta,
            media=self.media,
            action_checkbox_name=admin.ACTION_CHECKBOX_NAME,
            queryset=queryset,
        )

        return TemplateResponse(request, "admin/slate_picker.html", context=ctx)

    make_shows.short_description = 'Turn selected applications into shows'

    def create_shows_in(self, request, queryset):
        slate_pk = request.POST.get("slate")
        slate = ScheduleSlate.objects.get(pk=slate_pk)

        failed_apps = 0
        for show_app in queryset:
            show_app: ShowApplication = show_app
            if not show_app.is_accepted:
                failed_apps += 1
                continue

            # Show findin' logic! Look for any shows with the same name
            try:
                if show_app.connected_show is not None:
                    show = show_app.connected_show
                else:
                    show = Show.objects.get(name__iexact=show_app.name)

                show_app.update_show(show)
            except Show.MultipleObjectsReturned:
                # Multiple shows with the same name exist! Bail out.
                failed_apps += 1
                continue
            except Show.DoesNotExist:
                show = show_app.make_show()

            time_slot = show_app.assigned_slot
            start_time = time(hour=time_slot.hour)
            end_time = (datetime.combine(date.min, start_time) + timedelta(hours=1)).time()

            slot, created = ShowSlot.objects.get_or_create(
                defaults=dict(show=show),
                slate=slate,
                day=time_slot.day,
                start_time=start_time,
                end_time=end_time,
            )

            if not created:
                slot.show = show
                slot.save(update_fields=['show'])

            show_app.connected_show = show
            show_app.save(update_fields=['connected_show'])

        if failed_apps > 0:
            self.message_user(
                request,
                "{0}/{1} applications were skipped due to problems".format(failed_apps, queryset.count()),
                level=messages.WARNING
            )
        else:
            self.message_user(request, "Turned {0} applications into shows".format(queryset.count()),
                              level=messages.SUCCESS)

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
