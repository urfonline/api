from datetime import time, timedelta, datetime, date

from django.conf.urls import url
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

from api.shows.models import ScheduleSlate, ShowSlot, Show, DAYS_OF_WEEK
from .models import ShowApplication, TimeSlotRequest, ShowApplicationSettings, AVAILABLE_HOURS


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
            return queryset.filter(assigned_slot__isnull=False) | queryset.filter(biweekly_slot__isnull=False)
        if self.value() == '0':
            return queryset.filter(assigned_slot__isnull=True) & queryset.filter(biweekly_slot__isnull=True)

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
    def __init__(self, attrs=None):
        super().__init__(attrs)

        self.show_application = None

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            return ""

        slot = TimeSlotRequest.objects.get(pk=value)
        context = {
            'slot_request': slot,
            'slot_link': reverse('admin:applications_timeslotrequest_change', args=[slot.pk]),
            'taken': slot.is_taken(),
            'biweekly_available': self.show_application.biweekly
                                  and slot.is_taken()
                                  and slot.accepted_application.biweekly,
            'biweekly_taken': bool(slot.biweekly_partner),
            'slot_name': name,
        }

        if slot.is_taken():
            context['taken_by_self'] = slot.accepted_application == self.show_application
            context['biweekly_is_self'] = slot.biweekly_partner == self.show_application

        return mark_safe(render_to_string('admin/time_slot_widget.html', context))

class ShowApplicationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        obj = self.instance
        self.fields['first_slot_choice'].widget.show_application = obj
        self.fields['second_slot_choice'].widget.show_application = obj
        self.fields['third_slot_choice'].widget.show_application = obj

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
    list_filter = ('category', 'biweekly', AcceptedListFilter, HasShowListFilter,)
    ordering = ('-created_at',)

    actions = ('make_shows',)

    readonly_fields = (
        'name', 'host_name', 'contact_email', 'contact_phone',
        'cover', 'cover_width', 'cover_height',
        'banner', 'banner_width', 'banner_height',
        'link_to_biweekly_slot', 'created_at', 'link_to_connected_show'
    )

    fieldsets = (
        ('Applicant Info', {
            'fields': ('host_name', 'producer_name', 'contact_email', 'contact_phone', 'created_at', 'new_show')
        }),
        ('Basic Info', {
            'fields': ('name', 'short_description', 'long_description', 'brand_color', 'emoji_description', 'category')
        }),
        ('Slot Choices', {
            'fields': ('biweekly', 'first_slot_choice', 'second_slot_choice', 'third_slot_choice', 'assigned_slot',
                       'link_to_biweekly_slot')
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

    def link_to_biweekly_slot(self, obj):
        if not hasattr(obj, 'biweekly_slot'):
            return self.admin_site.empty_value_display

        link = reverse('admin:applications_timeslotrequest_change', args=[obj.biweekly_slot.id])
        return format_html('<a href="{}">{!s}</a>', link, obj.biweekly_slot)

    link_to_biweekly_slot.short_description = 'Even-week assigned slot'

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

            # Figure out if this show is biweekly & if it's odd or even week
            if show_app.biweekly:
                if hasattr(show_app, 'biweekly_slot'):
                    week = 2
                    time_slot = show_app.biweekly_slot
                else:
                    week = 1
                    time_slot = show_app.assigned_slot
            else:
                week = None
                time_slot = show_app.assigned_slot

            if time_slot is not None:
                start_time = time(hour=time_slot.hour)
                end_time = (datetime.combine(date.min, start_time) + timedelta(hours=1)).time()

                slot, created = ShowSlot.objects.get_or_create(
                    defaults=dict(show=show),
                    slate=slate,
                    day=time_slot.day,
                    start_time=start_time,
                    end_time=end_time,
                    week=week,
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
        biweekly = False
        drop = False

        for n in ('first', 'second', 'third'):
            if 'drop_{}_slot_choice_biweekly'.format(n) in request.POST:
                biweekly = True
                drop = True
            elif 'assign_{}_slot_choice_biweekly'.format(n) in request.POST:
                biweekly = True
            elif 'assign_{}_slot_choice'.format(n) in request.POST:
                pass
            else:
                continue

            choice = int(request.POST[n + '_slot_choice'])
            break

        if choice is not None:
            if biweekly:
                ts = TimeSlotRequest.objects.get(pk=choice)
                ts.biweekly_partner = None if drop else obj
                ts.save(update_fields=['biweekly_partner'])
            else:
                obj.assigned_slot = TimeSlotRequest.objects.get(pk=choice)
                obj.save(update_fields=['assigned_slot'])
            request.POST['_continue'] = ""

        return super().response_change(request, obj)

    def current_schedule_view(self, request):
        slots = TimeSlotRequest.objects.all()

        rows = {}
        for hour, _ in AVAILABLE_HOURS:
            rows[hour] = dict(
                slots=slots.filter(hour=hour).order_by('day'),
                human=time(hour).strftime("%I%p"),
            )

        ctx = dict(
            rows=rows,
            opts=self.model._meta,
            week=DAYS_OF_WEEK,
            title="Show applications calendar",
        )

        return TemplateResponse(request, 'admin/schedule.html', context=ctx)

    def get_urls(self):
        return [
            url(r'^current-schedule/$', self.current_schedule_view)
        ] + super().get_urls()


class SlotTakenListFilter(admin.SimpleListFilter):
    title = 'filled status'
    parameter_name = 'is_taken'

    def lookups(self, request, model_admin):
        return [
            ('1', _('Taken')),
            ('0', _('Free')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(accepted_application__isnull=False)
        elif self.value() == '0':
            return queryset.filter(accepted_application__isnull=True)

        return queryset

@register(TimeSlotRequest)
class TimeSlotRequestAdmin(admin.ModelAdmin):
    list_display = ('day', 'hour',)
    list_filter = ('day', SlotTakenListFilter,)
    ordering = ('day', 'hour',)
    readonly_fields = ('linked_application',)
    fields = ('day', 'hour', 'linked_application', 'biweekly_partner',)

    def linked_application(self, obj):
        if not obj.accepted_application:
            return self.admin_site.empty_value_display

        link = reverse('admin:applications_showapplication_change', args=[obj.accepted_application.id])
        return format_html('<a href="{}">{}</a>', link, obj.accepted_application.name)

    linked_application.short_description = 'Accepted application'

@register(ShowApplicationSettings)
class ShowApplicationSettingsAdmin(SingletonModelAdmin):
    pass
