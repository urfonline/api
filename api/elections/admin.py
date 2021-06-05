from django.contrib import admin

from .models import Position, Candidate


@admin.register(Position)
class PositionsAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position',)

    def get_queryset(self, request):
        query = super().get_queryset(request)

        return query.select_related('position')

