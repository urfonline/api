from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from api.core.utils import upload_to_content


def upload_to_profile_cover(instance, filename):
    return upload_to_content('users/covers', filename)


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)

    cover = models.ImageField(upload_to=upload_to_profile_cover, width_field='cover_width', height_field='cover_height',
                              blank=True)
    cover_width = models.IntegerField(blank=True, null=True)
    cover_height = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})
