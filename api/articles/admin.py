from django.contrib import admin
from django.contrib.admin import register

from .models import Article


@register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'tone', 'associated_show')
