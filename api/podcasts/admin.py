from django.contrib.admin import register, ModelAdmin

from api.podcasts.models import PodcastProvider, Podcast


@register(PodcastProvider)
class PodcastProviderAdmin(ModelAdmin):
    list_display = ('name', 'type',)
    search_fields = ('name',)

@register(Podcast)
class PodcastAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_public',)
    list_filter = ('is_public',)
    search_fields = ('name',)
    readonly_fields = ('name', 'description',)
    fieldsets = (
        ('Options', {
            'fields': ('name', 'slug', 'is_public', 'provider', 'podcast_id', 'playlist_id',)
        }),
        ('Details', {
            'description': "Details must be edited via the remote provider",
            'fields': ('description',)
        }),
    )
