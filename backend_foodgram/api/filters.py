from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    """Фильтр для рецептов по параметрам в списке покупок."""
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    author = filters.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_list'
    )
    FILTER_MAP = {
        'is_favorited': 'favorite__user',
        'is_in_shopping_cart': 'shopping_cart__user',
    }

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_list', 'tags')

    def filter_boolean_field(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            filter_param = self.FILTER_MAP.get(name)
            return queryset.filter(**{filter_param: self.request.user})
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов."""
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-startswith')
