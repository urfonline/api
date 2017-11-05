from django.db import models
from wagtail.wagtailimages.models import Image, AbstractImage, AbstractRendition
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class TimeStampedModel(models.Model):
    created_at = AutoCreatedField('created')
    updated_at = AutoLastModifiedField('updated_at')

    class Meta:
        abstract = True


class UrfImage(AbstractImage):

    admin_form_fields = Image.admin_form_fields + (

    )


class UrfRendition(AbstractRendition):
    image = models.ForeignKey(UrfImage, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
