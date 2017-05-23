from django.conf import settings
from django.db import models
from solo.models import SingletonModel

from api.core.models import TimeStampedModel

DAYS_OF_WEEK = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
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


class ShowCategory(models.Model):
    name = models.CharField(max_length=30, verbose_name='Name')
    slug = models.SlugField()

    def __str__(self):
        return self.name


class Show(TimeStampedModel, models.Model):
    name = models.CharField(max_length=80, verbose_name='Show Name', help_text='Name of the show')
    slug = models.SlugField()

    short_description = models.CharField(max_length=90, verbose_name='Short description', help_text='A tiny one-sentence tag line for the show')
    long_description = models.TextField(verbose_name='Long description', help_text='A long description for your show')
    category = models.ForeignKey(ShowCategory, blank=False, )

    cover = models.ImageField(width_field='cover_width', height_field='cover_height')
    cover_width = models.IntegerField(blank=True, null=True)
    cover_height = models.IntegerField(blank=True, null=True)

    banner = models.ImageField(blank=True, null=True, width_field='banner_width', height_field='banner_height')
    banner_width = models.IntegerField(blank=True, null=True)
    banner_height = models.IntegerField(blank=True, null=True)

    brand_color = models.CharField(max_length=6, verbose_name='Branding color', help_text='Color hex for show branding')
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

    def __str__(self):
        return self.name


class ShowSlot(TimeStampedModel, models.Model):
    show = models.ForeignKey(Show, null=False, related_name='slots')
    slate = models.ForeignKey(ScheduleSlate, null=False, related_name='slots')

    start_time = models.TimeField()
    end_time = models.TimeField()
    day = models.IntegerField(blank=False, null=False, choices=DAYS_OF_WEEK)

    @property
    def __str__(self):
        return '[{slate}] {show} at {start} on {day}'.format(
            show=self.show.name, slate=self.slate.name, start=self.start_time, day=DAYS[self.day]
        )


class ShowSeries(TimeStampedModel, models.Model):
    show = models.ForeignKey(Show, null=False, related_name='series')
    name = models.CharField(max_length=80, null=False)
    slug = models.SlugField()
    type = models.CharField(max_length=20, null=False, default='broadcast', choices=SERIES_TYPE)

    def __str__(self):
        return '{show} - {series} [{type}]'.format(show=self.show.name, series=self.name, type=self.type)


class ShowEpisode(TimeStampedModel, models.Model):
    show = models.ForeignKey(Show, null=False, related_name='episodes')
    series = models.ForeignKey(ShowSeries, null=False, related_name='episodes')

    name = models.CharField(max_length=80, null=False)
    slug = models.SlugField()

    cover = models.ImageField(blank=True, null=True, width_field='cover_width', height_field='cover_height')
    cover_width = models.IntegerField(blank=True, null=True)
    cover_height = models.IntegerField(blank=True, null=True)

    show_notes = models.TextField(blank=True, null=True)

    published_at = models.DateTimeField()
    run_time = models.PositiveIntegerField()
    audio_resource = models.FileField()
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


class ShowsConfiguration(SingletonModel):
    current_slate = models.ForeignKey(ScheduleSlate, blank=True, null=True)
    automation_show = models.ForeignKey(Show, blank=True, null=True)
    off_air = models.BooleanField(default=False)

    def __str__(self):
        return 'Shows Configuration'

    class Meta:
        verbose_name = "Shows Configuration"
