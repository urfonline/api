__all__ = ['PodcastEpisode', 'PodcastDetails']

class PodcastEpisode:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.description = kwargs.get("description")
        self.media_url = kwargs.get("media_url")
        self.created_at = kwargs.get("created_at")

        self.cover_url = kwargs.get("cover_url", None)
        self.duration = kwargs.get("duration", "Unknown")
        self.is_explicit = kwargs.get("explicit", False)
        self.external_urls = kwargs.get("external_urls", {})

class PodcastDetails:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.slug = None
        self.description = kwargs.get("description")
        self.cover_url = kwargs.get("cover_url", None)
        self.external_urls = kwargs.get("external_urls", {})
        self.episodes = kwargs.get("episodes", [])
