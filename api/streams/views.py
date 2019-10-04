from api.streams.models import StreamConfiguration
from django.http import HttpResponse
from django.http.request import HttpRequest
import requests

def get_stream_status(request: HttpRequest, stream_slug: str):
    stream = StreamConfiguration.objects.get(slug=stream_slug)

    r = requests.get(f'http://{stream.host}:{stream.port}/status-json.xsl')
    r.raise_for_status()

    return HttpResponse(r.json())
