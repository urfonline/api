from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import Event


class EventAdmin(ModelAdmin):
    model = Event
    menu_icon = 'book'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title', 'start_date')
    list_filter = ('start_date', )
    search_fields = ('title',)

modeladmin_register(EventAdmin)
