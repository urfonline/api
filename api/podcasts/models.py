from django.db import models
from django.utils.functional import cached_property

from api.podcasts.remote.interface import PodcastDetails
from .remote import sharpstream_v1, spotify

PROVIDER_TYPES = (
    ('sharpstream_v1', 'Sharpstream RSS API'),
    ('spotify', 'Spotify'),
)

PROVIDERS = {
    'sharpstream_v1': sharpstream_v1,
    'spotify': spotify,
}

class PodcastProvider(models.Model):
    name = models.CharField(max_length=60)
    type = models.CharField(max_length=60, choices=PROVIDER_TYPES, verbose_name='Podcasts Provider')
    api_key = models.CharField(max_length=200)
    client_id = models.IntegerField(verbose_name='Client ID')

    def fetch_podcast_details(self, podcast) -> PodcastDetails:
        return PROVIDERS[self.type].fetch_podcast_details(self, podcast)

    def __str__(self):
        return self.name

class Podcast(models.Model):
    name = models.CharField(max_length=70, blank=True)
    slug = models.SlugField(unique=True)
    provider = models.ForeignKey(PodcastProvider, on_delete=models.PROTECT)
    podcast_id = models.IntegerField(verbose_name='Podcast ID')
    playlist_id = models.IntegerField(verbose_name='Playlist ID')
    spotify_id = models.CharField(max_length=70, blank=True, null=True, verbose_name='Spotify show ID')
    is_public = models.BooleanField(verbose_name='visibility')

    def fetch_details(self) -> PodcastDetails:
        details = self.provider.fetch_podcast_details(self)
        details.slug = self.slug
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
