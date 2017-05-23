import os
import uuid


def upload_to_content(loc, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('content', loc, filename)
