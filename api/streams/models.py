from django.db import models

from api.shows.models import ScheduleSlate

class StreamConfiguration(models.Model):
    name = models.CharField(max_length=70, null=False)
    slug = models.SlugField(unique=True)
    host = models.CharField(max_length=80, null=False)
    port = models.IntegerField(blank=False, null=False)
    mountpoint = models.CharField(max_length=40, default="/stream", null=False)
    mobile_mountpoint = models.CharField(max_length=40, default="/mobile", null=False)
    proxy_url = models.CharField(max_length=70, default=None, null=True, blank=True)
    priority_online = models.IntegerField(blank=False, null=False, default=10, verbose_name="Online Priority")
    priority_offline = models.IntegerField(blank=False, null=False, default=3, verbose_name="Bed Priority")
    slate = models.ForeignKey(ScheduleSlate, null=True, blank=True, verbose_name="Active Slate")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Stream"
