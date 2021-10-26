import requests
from django.http import JsonResponse, Http404
from django.http.request import HttpRequest

from api.streams.models import StreamConfiguration

def process_response(stream: StreamConfiguration, data):
    if stream.type == "ICECAST":
        stats = data["icestats"]
        source = stats["source"]

        if isinstance(list, source):
            source = source[0]

        return {
            "offline": source is None,
            "description": source["server_description"] if source is not None else None,
        }
    elif stream.type == "SHARPSTREAM":
        return {
            "offline": False,
            "description": "SharpStream",
        }
    else:
        return {
            "offline": False,
            "description": None,
        }

def get_stream_status(request: HttpRequest, stream_slug: str):
    try:
        stream = StreamConfiguration.objects.get(slug=stream_slug)

        if stream.status_url == "" or stream.status_url is None:
            return JsonResponse(process_response(stream, {}))

        r = requests.get(stream.status_url, timeout=7)
    except StreamConfiguration.DoesNotExist:
        raise Http404("Stream with slug {0} does not exist.".format(stream_slug))
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Upstream request timed out"}, status=504)
    except requests.exceptions.RequestException:
        return JsonResponse({"error": "Upstream request failed"}, status=504)

    if r.status_code != requests.codes.ok:
        return JsonResponse({"error": "Upstream request failed"}, status=502)

    return JsonResponse(process_response(stream, r.json()))
