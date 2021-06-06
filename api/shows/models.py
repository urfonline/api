from datetime import date, timedelta
import math

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django_extensions.db.fields import AutoSlugField
from solo.models import SingletonModel

from api.core.models import TimeStampedModel
from api.core.utils import upload_to_content, validate_hex

DAYS_OF_WEEK = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
)

BIWEEKLY_OPTIONS = (
    (1, 'Odd Weeks'),
    (2, 'Even Weeks'),
)

DAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]

SERIES_TYPE = (
    ('broadcast', 'Broadcast'),
)

CREDIT_ROLES = (
    ('producer', 'Producer'),
    ('host', 'Host'),
    ('guest', 'Guest'),
    ('performer', 'Performer'),
    ('writer', 'Writer'),
)


def upload_to_show_cover(instance, filename):
    return upload_to_content('shows/covers', filename)


def upload_to_show_banner(instance, filename):
    return upload_to_content('shows/banners', filename)


def upload_to_episode_cover(instance, filename):
    return upload_to_content('episodes/covers', filename)


def upload_to_episode_audio(instance, filename):
    return upload_to_content('episodes/audio', filename)

def validate_monday(value: date):
    if value.weekday() != 0:
        raise ValidationError("%(value)s is not a Monday", params=dict(value=value))

class ShowCategory(models.Model):
    name = models.CharField(max_length=30, verbose_name='Name')
    slug = models.SlugField()
    color = models.CharField(default='', blank=True, max_length=6, verbose_name='Branding color', help_text='Color hex for category')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Show(TimeStampedModel, models.Model):
    name = models.CharField(max_length=80, verbose_name='Show Name', help_text='Name of the show')
    slug = AutoSlugField(unique=True, blank=False, editable=True, populate_from='name')

    short_description = models.CharField(max_length=90, verbose_name='Short description', help_text='A tiny one-sentence tag line for the show')
    long_description = models.TextField(verbose_name='Long description', help_text='A long description for your show')
    category = models.ForeignKey(ShowCategory, on_delete=models.CASCADE, blank=False, related_name='shows')

    cover = models.ImageField(null=True, blank=True, upload_to=upload_to_show_cover)
    cover_width = models.IntegerField(blank=True, null=True)
    cover_height = models.IntegerField(blank=True, null=True)

    banner = models.ImageField(upload_to=upload_to_show_banner, blank=True, null=True)
    banner_width = models.IntegerField(blank=True, null=True)
    banner_height = models.IntegerField(blank=True, null=True)

    brand_color = models.CharField(max_length=6, verbose_name='Branding color', help_text='Color hex for show branding',
                                   validators=[validate_hex])
    emoji_description = models.CharField(max_length=4, verbose_name='Emoji', help_text='Describe the show in a single emoji')

    has_interaction = models.BooleanField(default=False, verbose_name='Enable interaction',
                                          help_text='Enable interactive features in the player, such as highlighting '
                                                    'the sms number '
                                          )
    social_facebook_url = models.URLField(blank=True, null=True, verbose_name='Facebook URL')
    social_twitter_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Twitter handle')
    social_mixcloud_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Mixcloud handle')
    social_snapchat_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Snapchat handle')
    social_soundcloud_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Soundcloud handle')
    social_instagram_handle = models.CharField(max_length=35, blank=True, null=True, verbose_name='Instagram handle')
    social_youtube_url = models.URLField(blank=True, null=True, verbose_name='YouTube URL')

    def __str__(self):
        return self.name


class ScheduleSlate(TimeStampedModel, models.Model):
    name = models.CharField(max_length=5, null=False)
    notes = models.TextField(blank=True, null=True)
    automation_show = models.ForeignKey(Show, on_delete=models.SET_NULL, blank=False, null=True)
    broadcast_start_date = models.DateField(verbose_name="Broadcasting Start Date", validators=[validate_monday])

    def __str__(self):
        return self.name

    def get_shows(self):
        return Show.objects.filter(slots__slate=self).select_related('category').distinct()

    @property
    def week_from_start(self):
        """
        Get the week number (1-indexed) based on the start of broadcasting date
        :return: Week of broadcast calendar, starting at 1
        """
        diff = date.today() - self.broadcast_start_date
        return math.floor(diff / timedelta(days=7)) + 1

    class Meta:
        verbose_name = 'slate'


class ShowSlot(TimeStampedModel, models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, null=False, related_name='slots')
    slate = models.ForeignKey(ScheduleSlate, on_delete=models.CASCADE, null=False, related_name='slots')

    start_time = models.TimeField()
    end_time = models.TimeField()
    day = models.IntegerField(blank=False, null=False, choices=DAYS_OF_WEEK)
    week = models.IntegerField(blank=True, null=True, choices=BIWEEKLY_OPTIONS, default=None)

    def __str__(self):
        return '[{slate}] {show} at {start} on {day}'.format(
            show=self.show.name, slate=self.slate.name, start=self.start_time, day=DAYS[self.day]
        )

    @property
    def name(self):
        return "[{slate.name}] {show.name}".format(slate=self.slate, show=self.show)

    def validate_unique(self, exclude=None):
        if ShowSlot.objects.exclude(id=self.id)\
            .filter(slate=self.slate, day=self.day, start_time=self.start_time, end_time=self.end_time,
                    week__isnull=True)\
            .exists():
            raise ValidationError("Duplicate slot for this slate: check that a slot with this day & time doesn't exist "
                                  "already")

        return super().validate_unique(exclude)

    class Meta:
        verbose_name = 'slot'
        unique_together = ('slate', 'week', 'day', 'start_time', 'end_time',)


class ShowSeries(TimeStampedModel, models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, null=False, related_name='series')
    name = models.CharField(max_length=80, null=False)
    slug = models.SlugField()
    type = models.CharField(max_length=20, null=False, default='broadcast', choices=SERIES_TYPE)

    def __str__(self):
        return '{show} - {series} [{type}]'.format(show=self.show.name, series=self.name, type=self.type)

    class Meta:
        verbose_name = 'series'
        verbose_name_plural = 'series'


class ShowEpisode(TimeStampedModel, models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, null=False, related_name='episodes')
    series = models.ForeignKey(ShowSeries, on_delete=models.CASCADE, null=False, related_name='episodes')

    name = models.CharField(max_length=80, null=False)
    slug = models.SlugField()

    cover = models.ImageField(upload_to=upload_to_episode_cover, blank=True, null=True)
    cover_width = models.IntegerField(blank=True, null=True)
    cover_height = models.IntegerField(blank=True, null=True)

    show_notes = models.TextField(blank=True, null=True)

    published_at = models.DateTimeField()
    run_time = models.PositiveIntegerField()
    audio_resource = models.FileField(upload_to=upload_to_episode_audio)
    credits = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='EpisodeCredit',
                                     through_fields=('episode', 'user', )
                                     )

    def __str__(self):
        return '{show} - {series}, {episode_name}'.format(
            show=self.show.name,
            series=self.series.name,
            episode_name=self.name
        )

    class Meta:
        verbose_name = 'episode'
        verbose_name_plural = 'episodes'


class EpisodeCredit(models.Model):
    episode = models.ForeignKey(ShowEpisode, db_index=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='credits', db_index=True, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, null=False, choices=CREDIT_ROLES)

    def __str__(self):
        return '{user} credited as {role} on {episode}'.format(
            user=self.user,
            role=self.role,
            episode=self.episode,
        )

    class Meta:
        verbose_name = 'Episode Credit'


class ShowsConfiguration(SingletonModel):
    current_slate = models.ForeignKey(ScheduleSlate, on_delete=models.SET_NULL, blank=True, null=True)
    automation_show = models.ForeignKey(Show, on_delete=models.SET_NULL, blank=True, null=True)
    off_air = models.BooleanField(default=False)

    def __str__(self):
        return 'Shows Settings'

    class Meta:
        verbose_name = 'Shows Settings'
