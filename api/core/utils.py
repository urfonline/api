import os
import uuid
import math

from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def upload_to_content(loc, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('content', loc, filename)

def validate_hex(value: str):
    try:
        int(value, 16)
    except ValueError:
        raise ValidationError(
            _('Invalid hex code %(value)s!'),
            params={'value': value}
        )

def format_delta(value: timedelta):
    seconds = int(value.total_seconds())

    minutes = math.floor(seconds / 60)
    remaining = seconds % 60

    return f"{minutes:d}:{remaining:02d}"
