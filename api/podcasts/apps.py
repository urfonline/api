from django.apps import AppConfig


class PodcastConfig(AppConfig):
    name = 'api.podcasts'
    verbose_name = 'Podcasts'

    def ready(self):
        from . import signals
