from django.conf import settings
from django.db import models
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel, \
    FieldRowPanel, ObjectList
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel

from api.core.models import TimeStampedModel
from api.core.utils import upload_to_content
from api.core.models import UrfImage

ARTICLE_TONES = (
    ('INTERVIEW', 'Interview'),
    ('PREVIEW', 'Preview'),
    ('REVIEW', 'Review'),
    ('OPINION', 'Opinion'),
    ('ANNOUNCEMENT', 'Announcement'),
    ('BLOG', 'Blog'),
)


def upload_to_article_featured(instance, filename):
    return upload_to_content('articles/featured', filename)


class Article(TimeStampedModel, models.Model):
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='articles', db_index=True)
    associated_show = models.ForeignKey('shows.Show', blank=True, null=True, related_name='articles', db_index=True, on_delete=models.CASCADE)

    title = models.CharField(max_length=120, blank=False, null=False)
    slug = models.SlugField()

    featured_image = models.ForeignKey(UrfImage, on_delete=models.SET_NULL, blank=True, null=True)
    short_description = models.TextField(blank=False)

    tone = models.CharField(max_length=20, default='BLOG', choices=ARTICLE_TONES)

    published_at = models.DateTimeField(blank=True, null=True, default=None)

    content = RichTextField(null=False, blank=False, default='')

    custom_panels = [
        MultiFieldPanel([
            FieldPanel('title', classname='title'),
            FieldPanel('authors'),
            FieldPanel('slug'),
            FieldPanel('associated_show'),
            FieldPanel('tone'),
            FieldRowPanel([
                FieldPanel('published_at'),
            ]),
        ], heading='The basics'),
        MultiFieldPanel([
            ImageChooserPanel('featured_image'),
            FieldPanel('short_description'),
            FieldPanel('content'),
        ], heading='Content'),
    ]

    edit_handler = ObjectList(custom_panels)

    def __str__(self):
        return self.title
