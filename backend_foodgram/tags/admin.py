from django.contrib.admin import ModelAdmin, register

from tags.models import Tag


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug')
