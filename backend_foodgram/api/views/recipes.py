from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from api.permissions import IsAuthorOrReadOnly
from api.paginations import CustomPageNumberPagination
from api.serializers.recipes import (
    FavoriteSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    IngredientSerializer,
    FullRecipeInfoSerializer
)
from recipes.models import (
    Recipe, RecipeIngredient, Favorite, ShoppingCart, Tag, Ingredient
)
from api.filters import IngredientFilter, RecipeFilter


class ModelFunctionality:
    def create_model(self, request, instance, serializer_name):
        """Метод для добавления модели."""
        serializer = serializer_name(
            data={'user': request.user.id, 'recipe': instance.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_model(self, request, model_name, instance, error_message):
        """Метод для удаления модели."""
        if not model_name.objects.filter(user=request.user, recipe=instance).exists():
            return Response({'errors': error_message}, status=status.HTTP_400_BAD_REQUEST)
        model_name.objects.filter(user=request.user, recipe=instance).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обработки запросов на получение ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обработки запросов на получение тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(ModelFunctionality, viewsets.ModelViewSet):
    """
    Вьюсет для работы с рецептами.
    Обработка запросов создания/получения/редактирования/удаления рецептов
    Добавление/удаление рецепта в избранное и список покупок.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete'
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FullRecipeInfoSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.create_model(
                request,
                recipe,
                FavoriteSerializer
            )

        if request.method == 'DELETE':
            error_message = 'Такого рецепта нет в избранном.'
            return self.delete_model(
                request,
                Favorite,
                recipe,
                error_message
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        """Удаление/добавление в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.create_model(
                request,
                recipe,
                ShoppingCartSerializer
            )

        if request.method == 'DELETE':
            error_message = 'Такого рецепта нет в списке покупок.'
            return self.delete_model(
                request,
                ShoppingCart,
                recipe,
                error_message
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Скачивание файла со списком покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_cart = [
            'Список покупок:\n'
        ]
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_cart.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
