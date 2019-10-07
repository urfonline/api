from api.streams.models import StreamConfiguration
from django.http import JsonResponse, Http404
from django.http.request import HttpRequest
import requests

def get_stream_status(request: HttpRequest, stream_slug: str):
    try:
        stream = StreamConfiguration.objects.get(slug=stream_slug)

        r = requests.get('http://{stream.host}:{stream.port}/status-json.xsl'.format(stream=stream), timeout=5)
    except StreamConfiguration.DoesNotExist:
        raise Http404("Stream with slug {0} does not exist.".format(stream_slug))
    except requests.exceptions.Timeout:
        return JsonResponse({ "error": "Upstream request timed out" }, status=504)

    if r.status_code != requests.codes.ok:
        return JsonResponse({ "error": "Upstream request failed" }, status=502)

    return JsonResponse(r.json())
