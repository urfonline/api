from api.streams.models import StreamConfiguration
from django.http import JsonResponse
from django.http.request import HttpRequest
import requests

def get_stream_status(request: HttpRequest, stream_slug: str):
    stream = StreamConfiguration.objects.get(slug=stream_slug)

    r = requests.get('http://{stream.host}:{stream.port}/status-json.xsl'.format(stream=stream))
    r.raise_for_status()

    return JsonResponse(r.json())
