from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

POSITIONS = (
    ('HERO', 'Hero'),
    ('SEC_1', 'Secondary 1'),
    ('SEC_2', 'Secondary 2'),
)


class HomepageBlock(models.Model):
    limit = models.Q(app_label='shows', model='show') | models.Q(app_label='articles',
                                                                model='article') | models.Q(
        app_label='events', model='event')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    published_at = models.DateTimeField()

    position = models.CharField(max_length=12, choices=POSITIONS)
