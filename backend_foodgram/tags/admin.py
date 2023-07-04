from django.contrib.admin import ModelAdmin, register
from django.conf import settings

from tags.models import Tag


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = settings.EMPTY_VALUE
