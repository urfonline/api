from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page

from api.podcasts.remote.interface import PodcastDetails
from .remote import spotify, timbre

PROVIDER_TYPES = (
    ('sharpstream_v1', 'Sharpstream RSS API'),
    ('spotify', 'Spotify'),
    ('timbre', 'Timbre (Sharpstream)'),
)

PROVIDERS = {
    'sharpstream_v1': None,
    'spotify': spotify,
    'timbre': timbre,
}

class PodcastProvider(models.Model):
    name = models.CharField(max_length=60)
    type = models.CharField(max_length=60, choices=PROVIDER_TYPES, verbose_name='Podcasts Provider')
    api_key = models.CharField(max_length=4096)

    def fetch_podcast_details(self, podcast) -> PodcastDetails:
        return PROVIDERS[self.type].fetch_podcast_details(self, podcast)

    def __str__(self):
        return self.name

class Podcast(models.Model):
    name = models.CharField(max_length=70, blank=True)
    slug = models.SlugField(unique=True)
    provider = models.ForeignKey(PodcastProvider, on_delete=models.PROTECT)
    remote_id = models.CharField(max_length=200, verbose_name='Provider ID of the podcast')
    spotify_id = models.CharField(max_length=70, blank=True, null=True, verbose_name='Spotify show ID')
    is_public = models.BooleanField(verbose_name='visibility')

    def fetch_details(self) -> PodcastDetails:
        details = self.provider.fetch_podcast_details(self)
        details.slug = self.slug

        if self.spotify_url is not None and 'spotify' not in details.external_urls:
            details.external_urls['spotify'] = self.spotify_url

        return details

    cached_details = cached_property(fetch_details, name='cached_details')

    @property
    def description(self):
        return self.cached_details.description

    @property
    def spotify_url(self):
        if self.spotify_id is not None:
            return f"https://open.spotify.com/show/{self.spotify_id}"
        else:
            return None

    def __str__(self):
        return self.name

class PodcastHomePage(Page):
    subpage_types = ['PodcastPage']
    max_count = 1

class PodcastPage(Page):
    body = RichTextField()

    subpage_types = []
    parent_page_types = ['PodcastHomePage']

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    api_fields = [
        APIField('body'),
    ]
