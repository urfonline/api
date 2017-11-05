from django.db import models
from wagtail.wagtailadmin.edit_handlers import MultiFieldPanel, FieldPanel, FieldRowPanel, \
    ObjectList
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from api.core.models import UrfImage


class Event(models.Model):
    title = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    short_description = models.TextField(blank=False)
    location = models.TextField(blank=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    associated_show = models.ForeignKey('shows.Show', blank=True, null=True, related_name='events', db_index=True, on_delete=models.CASCADE)

    facebook_event = models.URLField(default='', blank=True, verbose_name='Facebook Event URL')
    ussu_event = models.URLField(default='', blank=True, verbose_name='Students Union Event Page URL')

    featured_image = models.ForeignKey(
        UrfImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    custom_panels = [
        MultiFieldPanel([
            FieldPanel('title', classname='title'),
            FieldPanel('slug'),
            FieldRowPanel([
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ]),
            FieldPanel('location'),
            FieldPanel('associated_show'),
        ], heading='The basics'),
        MultiFieldPanel([
            ImageChooserPanel('featured_image'),
            FieldPanel('short_description'),
            FieldPanel('description'),
        ], heading='Content'),
        MultiFieldPanel([
            FieldPanel('facebook_event'),
            FieldPanel('ussu_event'),
        ], heading='Content'),
    ]

    edit_handler = ObjectList(custom_panels)

    def __str__(self):
        return self.title
