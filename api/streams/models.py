from django.db import models

from api.shows.models import ScheduleSlate

STREAM_TYPES = [
    ("ICECAST", "Icecast"),
    ("SHARPSTREAM", "SharpStream"),
]

class StreamConfiguration(models.Model):
    name = models.CharField(max_length=70, null=False)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=STREAM_TYPES)
    proxy_url = models.CharField(max_length=70, default=None, null=True, blank=True, verbose_name="Stream URL")
    status_url = models.CharField(max_length=70, default=None, null=True, blank=True, verbose_name="Status URL")
    api_key = models.CharField(max_length=4096, default=None, null=True, blank=True, verbose_name="API key",
                               help_text="API key for status queries for providers that require it.")
    priority_online = models.IntegerField(blank=False, null=False, default=10, verbose_name="Online Priority")
    priority_offline = models.IntegerField(blank=False, null=False, default=3, verbose_name="Bed Priority")
    slate = models.ForeignKey(ScheduleSlate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Active Slate")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Stream"
