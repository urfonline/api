from datetime import datetime, timedelta
from tekore import request_client_token, Spotify
from tekore.model import SimpleEpisode, ReleaseDatePrecision

from api.core.utils import format_delta
from api.podcasts.remote.interface import PodcastDetails, PodcastEpisode

class SpotifyClient:
    instance = None

    def __init__(self, api_key):
        client_id, client_secret = api_key.split(':')
        self.token = request_client_token(client_id, client_secret)
        self.spotify = Spotify(self.token)

    @classmethod
    def get(cls, api_key):
        if cls.instance is None:
            cls.instance = SpotifyClient(api_key)

        return cls.instance

def parse_spotify_date(date_str: str, precision: ReleaseDatePrecision):
    if precision is ReleaseDatePrecision.day:
        return datetime.strptime(date_str, "%Y-%m-%d")
    elif precision is ReleaseDatePrecision.month:
        return datetime.strptime(date_str, "%Y-%m")
    else:
        return datetime.strptime(date_str, "%Y")

def map_episode(episode: SimpleEpisode):
    return PodcastEpisode(title=episode.name, description=episode.description, media_url=episode.audio_preview_url,
                          cover_url=max(episode.images, key=lambda i: i.width).url,
                          created_at=parse_spotify_date(episode.release_date, episode.release_date_precision),
                          duration=format_delta(timedelta(milliseconds=episode.duration_ms)), explicit=episode.explicit,
                          external_urls=episode.external_urls)

def fetch_podcast_details(provider, podcast):
    client = SpotifyClient.get(provider.api_key)

    show = client.spotify.show(podcast.spotify_id, market="gb")
    episodes = client.spotify.all_items(show.episodes)

    mapped_eps = list(map(map_episode, episodes))

    return PodcastDetails(title=show.name, description=show.description, episodes=mapped_eps,
                          cover_url=max(show.images, key=lambda i: i.width).url, external_urls=show.external_urls)
