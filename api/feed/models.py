from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from api.core.models import TimeStampedModel

ACTION_CHOICES = (
    ('NEW_EPISODE', 'New episode'),
    ('NEW_ARTICLE', 'New article'),
    ('NEW_EVENT', 'New event'),
    ('NEW_SHOW', 'New Show'),
)


class Activity(TimeStampedModel, models.Model):
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, null=False, blank=False)

    prop_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    prop_object_id = models.PositiveIntegerField()
    prop_content_object = GenericForeignKey('prop_content_type', 'prop_object_id')
