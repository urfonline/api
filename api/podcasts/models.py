from django.db import models

from api.podcasts.remote.interface import PodcastDetails
from .remote import sharpstream_v1

PROVIDER_TYPES = (
    ('sharpstream_v1', 'Sharpstream RSS API'),
)

PROVIDERS = {
    'sharpstream_v1': sharpstream_v1,
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
    is_public = models.BooleanField(verbose_name='visibility')

    def fetch_details(self) -> PodcastDetails:
        return self.provider.fetch_podcast_details(self)

    def __str__(self):
        return self.name
