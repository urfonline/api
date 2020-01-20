from django.core.files.storage import default_storage
from django.http import JsonResponse

from api.shows.models import upload_to_show_cover, upload_to_show_banner


def upload_cover(request):
    if request.method == 'POST':
        file = request.FILES.items()[0]
        filename = upload_to_show_cover(None, file.name)

        default_storage.save(filename, file)

        return JsonResponse({'success': True, 'filename': filename})

def upload_banner(request):
    if request.method == 'POST':
        file = request.FILES.items()[0]
        filename = upload_to_show_banner(None, file.name)

        default_storage.save(filename, file)

        return JsonResponse({'success': True, 'filename': filename})
