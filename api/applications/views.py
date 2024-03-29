from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.applications.models import ShowApplicationSettings
from api.shows.models import upload_to_show_cover, upload_to_show_banner

def verify_origin(request):
    origin = request.META.get("HTTP_ORIGIN")

    return origin in settings.CORS_ORIGIN_WHITELIST

@csrf_exempt
def upload_cover(request):
    if not verify_origin(request):
        return JsonResponse({'success': False, 'message': "Invalid origin"})

    cfg = ShowApplicationSettings.get_solo()
    if not cfg.applications_open:
        return JsonResponse({'success': False, 'message': "Show applications not open."})

    if request.method == 'POST':
        file = request.FILES['file']
        filename = upload_to_show_cover(None, file.name)

        default_storage.save(filename, file)

        return JsonResponse({'success': True, 'filename': filename})

@csrf_exempt
def upload_banner(request):
    if not verify_origin(request):
        return JsonResponse({'success': False, 'message': "Invalid origin"})

    cfg = ShowApplicationSettings.get_solo()
    if not cfg.applications_open:
        return JsonResponse({'success': False, 'message': "Show applications not open."})

    if request.method == 'POST':
        file = request.FILES['file']
        filename = upload_to_show_banner(None, file.name)

        default_storage.save(filename, file)

        return JsonResponse({'success': True, 'filename': filename})
