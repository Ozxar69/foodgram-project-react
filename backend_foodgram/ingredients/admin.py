from django.contrib.admin import ModelAdmin, register
from django.conf import settings

from ingredients.models import Ingredient


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = settings.EMPTY_VALUE

