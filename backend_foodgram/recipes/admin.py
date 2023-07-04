from django.contrib.admin import ModelAdmin, register, TabularInline
from django.conf import settings

from recipes.models import (
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingCart
)


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'favorites_amount'
    )
    list_filter = ('name', 'author', 'tags')
    empty_value_display = settings.EMPTY_VALUE
    inlines = [
        RecipeIngredientInline,
    ]

    def favorites_amount(self, obj):
        return obj.favorite_recipe.count()


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    empty_value_display = settings.EMPTY_VALUE


@register(FavoriteRecipe)
class FavoriteRecipeAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = settings.EMPTY_VALUE


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = settings.EMPTY_VALUE
