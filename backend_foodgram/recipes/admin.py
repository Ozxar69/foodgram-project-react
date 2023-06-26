from django.contrib.admin import ModelAdmin, register

from recipes.models import (
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingList
)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'display_tags', 'favorite', 'pub_date')
    list_filter = ('name', 'author', 'tags')
    search_filter = ('name',)
    readonly_fields = ('favorite',)
    fields = (
        'image',
        ('name', 'author'),
        'description',
        ('tags', 'cook_time'),
        'favorite',
    )

    def display_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Теги'

    def favorite(self, obj):
        return obj.favorite_recipe.count
    favorite.short_description = 'Добавлен в избранное'


@register(RecipeIngredient)
class RecipeIngredientsAdmin(ModelAdmin):
    list_display = ('recipe', 'ingredient', 'count')


@register(FavoriteRecipe)
class FavoriteRecipeAdmin(ModelAdmin):
    list_display = ('recipe', 'user')


@register(ShoppingList)
class ShoppingListAdmin(ModelAdmin):
    list_display = ('recipe', 'user')
