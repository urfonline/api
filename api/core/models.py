from django.db import models
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class TimeStampedModel(models.Model):
    created_at = AutoCreatedField('created')
    updated_at = AutoLastModifiedField('updated_at')

    class Meta:
        abstract = True
