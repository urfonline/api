from django.db.models.signals import pre_save
from django.dispatch import receiver

from api.podcasts.models import Podcast

@receiver(pre_save, sender=Podcast)
def on_pre_save(instance: Podcast, **kwargs):
    instance.name = instance.fetch_details().title
