from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import Article


class ArticleAdmin(ModelAdmin):
    model = Article
    menu_icon = 'book'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title', 'authors', 'created_at', 'published_at')
    list_filter = ('published_at', )
    search_fields = ('title',)

modeladmin_register(ArticleAdmin)
