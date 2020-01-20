from django.db import models
from solo.models import SingletonModel

from api.core.models import TimeStampedModel
from api.core.utils import validate_hex
from api.shows.models import ShowCategory, upload_to_show_cover, upload_to_show_banner, DAYS_OF_WEEK, ShowSlot
from api.users.models import User

from datetime import time, datetime

_AVAILABLE_HOURS = [0] + list(range(8, 24))
AVAILABLE_HOURS = list(
    map(
        lambda n: (n, time(n).strftime("%H:%M"),),
        _AVAILABLE_HOURS
    )
)

# Like a ShowSlot, but not tied to any slate & no duration (assumed to be 1 hour)
class TimeSlotRequest(models.Model):
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    hour = models.IntegerField(choices=AVAILABLE_HOURS)

    def is_taken(self):
        return self.accepted_application is not None

    def fetch_slot(self, slate):
        return ShowSlot.objects.get(slate=slate, day=self.day,
                                    start_time__hour=self.hour,
                                    end_time__hour=self.hour + 1)

    def __str__(self):
        # is this a hack? maybe
        return datetime(year=1979, month=1, day=self.day+1, hour=self.hour).strftime("%A at %H:%M")

    class Meta:
        verbose_name = 'Time Slot Request'
        verbose_name_plural = 'Time Slot Requests'

class ShowApplication(TimeStampedModel, models.Model):
    name = models.CharField(max_length=80, verbose_name='Show Name', help_text='Name of the show')
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='show_applications')
    contact_email = models.EmailField()
    short_description = models.CharField(max_length=90, verbose_name='Short description',
                                         help_text='A tiny one-sentence tag line for the show')
    long_description = models.TextField(verbose_name='Long description', help_text='A long description for your show')
    category = models.ForeignKey(ShowCategory, blank=False, null=True, on_delete=models.SET_NULL,
                                 related_name='show_applications')

    cover = models.ImageField(null=True, blank=True, upload_to=upload_to_show_cover, width_field='cover_width',
                              height_field='cover_height')
    cover_width = models.IntegerField(blank=True, null=True)
    cover_height = models.IntegerField(blank=True, null=True)

    banner = models.ImageField(upload_to=upload_to_show_banner, blank=True, null=True, width_field='banner_width',
                               height_field='banner_height')
    banner_width = models.IntegerField(blank=True, null=True)
    banner_height = models.IntegerField(blank=True, null=True)

    brand_color = models.CharField(max_length=6, verbose_name='Branding color', help_text='Color hex for show branding',
                                   validators=[validate_hex])
    emoji_description = models.CharField(max_length=4, verbose_name='Emoji',
                                         help_text='Describe the show in a single emoji')

    first_slot_choice = models.ForeignKey(TimeSlotRequest, on_delete=models.PROTECT,
                                          verbose_name='First Slot Choice',
                                          related_name='first_choice_applications')
    second_slot_choice = models.ForeignKey(TimeSlotRequest, on_delete=models.PROTECT,
                                           verbose_name='Second Slot Choice',
                                           related_name='second_choice_applications')
    third_slot_choice = models.ForeignKey(TimeSlotRequest, on_delete=models.PROTECT,
                                          verbose_name='Third Slot Choice',
                                          related_name='third_choice_applications')

    social_facebook_url = models.URLField(blank=True, null=True, verbose_name='Facebook URL')
    social_twitter_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Twitter handle')
    social_mixcloud_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Mixcloud handle')
    social_snapchat_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Snapchat handle')
    social_soundcloud_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Soundcloud handle')
    social_instagram_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Instagram handle')
    social_youtube_url = models.URLField(blank=True, null=True, verbose_name='YouTube URL')

    assigned_slot = models.OneToOneField(TimeSlotRequest, blank=True, null=True, on_delete=models.SET_NULL,
                                         verbose_name='Assigned Slot',
                                         help_text='Exec\'s slot choice for this application',
                                         related_name='accepted_application')

    @property
    def user_name(self):
        if self.owner is None:
            return "-"
        else:
            return self.owner.name

    @property
    def is_accepted(self):
        return self.assigned_slot is not None

    class Meta:
        verbose_name = 'Show Application'
        verbose_name_plural = 'Show Applications'

class ShowApplicationSettings(SingletonModel):
    applications_open = models.BooleanField(default=False)
    apply_page_subtitle = models.TextField(blank=True, verbose_name="Application Page Subtitle")

    class Meta:
        verbose_name = "Show Applications Settings"
