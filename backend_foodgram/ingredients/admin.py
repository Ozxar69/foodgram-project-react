from django.contrib.admin import ModelAdmin, register

from ingredients.models import Ingredient


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
