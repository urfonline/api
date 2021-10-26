from django.core.cache import cache

from .models import PodcastProvider
from .remote.interface import PodcastDetails
from .remote.timbre import fetch_podcasts, fetch_podcast

__all__ = ['fetch_cached_podcasts', 'fetch_cached_podcast']

CACHE_KEY = "76_timbre_feeds"

def fetch_cached_podcasts() -> list[PodcastDetails]:
    cached_feeds = cache.get(CACHE_KEY)

    if cached_feeds is None:
        provider = PodcastProvider.objects.get(type="timbre")

        cached_feeds = list(fetch_podcasts(provider))
        cache.set(CACHE_KEY, cached_feeds, 600)

    return cached_feeds

def fetch_cached_podcast(slug) -> PodcastDetails:
    key = f"{CACHE_KEY}:{slug}"
    cached_podcast = cache.get(key)

    if cached_podcast is None:
        provider = PodcastProvider.objects.get(type="timbre")

        cached_podcast = fetch_podcast(provider, slug)
        cache.set(key, cached_podcast, 300)

    return cached_podcast
