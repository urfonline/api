from datetime import datetime, timedelta
from typing import Iterator, Optional

import requests

from api.core.utils import format_delta
from api.podcasts.remote.interface import PodcastDetails, PodcastEpisode

__all__ = ['fetch_podcasts', 'fetch_podcast']

def item_to_episode(item) -> PodcastEpisode:
    duration = float(item["storage"]["ffmpeg_details"]["duration"])
    duration = format_delta(timedelta(seconds=duration))

    return PodcastEpisode(title=item["name"], description=item["description"], media_url=item["storage_file_url"],
                          created_at=datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                          cover_url=item["artwork"]["path"], duration=duration)

def feed_to_podcast(feed, include_episodes=False) -> PodcastDetails:
    external_urls = feed["external_links"] or []

    details = PodcastDetails(title=feed["name"], description=feed["description"], cover_url=feed["artwork"]["path"],
                             external_urls={item["id"]: item["url"] for item in external_urls})
    details.slug = feed["slug"]
    details.external_urls["rss"] = feed["feed_xml_file_url"]

    if include_episodes:
        details.episodes = list(map(item_to_episode, feed["items"]))

    return details

def fetch_podcasts(provider) -> Iterator[PodcastDetails]:
    headers = {
        "Authorization": f"Bearer {provider.api_key}",
        "Accept": "application/json",
    }

    params = {
        "filters": "sync_to_website:eq:1"
    }

    r = requests.get("https://timbrecms.sharp-stream.com/api/v1/feeds", headers=headers, params=params)
    r.raise_for_status()

    feeds = r.json()
    return map(feed_to_podcast, feeds["data"])

def fetch_podcast(provider, slug) -> Optional[PodcastDetails]:
    headers = {
        "Authorization": f"Bearer {provider.api_key}",
        "Accept": "application/json",
    }

    params = {
        "with_items": 1,
        "filters": f"slug:eq:{slug}",
    }

    r = requests.get(f"https://timbrecms.sharp-stream.com/api/v1/feeds", headers=headers, params=params)
    r.raise_for_status()

    feeds = r.json()["data"]

    if len(feeds) == 0:
        return None

    return feed_to_podcast(feeds[0], include_episodes=True)
