from django.db import models

class StreamConfiguration(models.Model):
    name = models.CharField(max_length=70, null=False)
    host = models.CharField(max_length=80, null=False)
    port = models.IntegerField(blank=False, null=False)
    mountpoint = models.CharField(max_length=40, default="/stream", null=False)
    priority_online = models.IntegerField(blank=False, null=False, default=10, verbose_name="Online Priority")
    priority_offline = models.IntegerField(blank=False, null=False, default=3, verbose_name="Offline Priority")
    metadata_source = models.CharField(null=False, choices=(("slate", "Active Slate"), ("icecast", "Icecast")), max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Stream"
