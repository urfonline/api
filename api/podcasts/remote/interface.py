__all__ = ['PodcastEpisode', 'PodcastDetails']

class PodcastEpisode:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.description = kwargs.get("description")
        self.media_url = kwargs.get("media_url")

        self.cover_url = kwargs.get("cover_url", None)
        self.duration = kwargs.get("duration", "Unknown")
        self.is_explicit = kwargs.get("explicit", False)

class PodcastDetails:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.description = kwargs.get("description")
        self.cover_url = kwargs.get("cover_url", None)
        self.episodes = kwargs.get("episodes", [])
