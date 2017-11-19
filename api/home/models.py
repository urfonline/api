from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

POSITIONS = (
    ('HERO', 'Hero'),
    ('SEC_1', 'Secondary 1'),
    ('SEC_2', 'Secondary 2'),
    ('THIRD_1', 'Third 1'),
    ('THIRD_2', 'Third 2'),
    ('THIRD_3', 'Third 3'),
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

    override_kicker = models.CharField(max_length=64, default='')
    override_title = models.CharField(max_length=265, default='')
    override_description = models.TextField(default='')
    override_background_color = models.CharField(max_length=64, default='')
