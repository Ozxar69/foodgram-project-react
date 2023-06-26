from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from reportlab.pdfgen import canvas
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics, ttfonts

from api.permissions import IsAuthorOrReadOnly
from api.paginations import CustomPageNumberPagination
from api.serializers.recipes import (
    FavoriteSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    TagSerializer
)
from api.serializers.ingredients import IngredientSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from api.filters import IngredientFilter, RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    def post_delete(self, pk, serializer_class, action_type):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user,
            recipe=recipe
        )
        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe':pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Такого рецепта не существует'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True)
    def action(self, request, pk, action_type):
        if action_type == 'favorite':
            serializer_class = FavoriteSerializer
        elif action_type == 'shopping_list':
            serializer_class = ShoppingListSerializer
        else:
            return Response({'error': 'Некорректный тип действия'},
                            status=status.HTTP_400_BAD_REQUEST)
        return self.post_delete_action(pk, serializer_class, action_type)

    @action(detail=False)
    def download_shopping_list(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            "attachment; filename='shopping_cart.pdf'"
        )
        p = canvas.Canvas(response)
        arial = ttfonts.TTFont('Arial', 'data/arial.ttf')
        pdfmetrics.registerFont(arial)
        p.setFont('Arial', 14)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=request.user).values_list(
            'ingredient__name', 'amount', 'ingredient__measurement_unit')

        ingr_list = {}
        for name, amount, unit in ingredients:
            if name not in ingr_list:
                ingr_list[name] = {'amount': amount, 'unit': unit}
            else:
                ingr_list[name]['amount'] += amount
        height = 700
        p.drawString(100, 750, 'Список покупок')
        for i, (name, data) in enumerate(ingr_list.items(), start=1):
            p.drawString(
                80, height,
                f"{i}. {name} – {data['amount']} {data['unit']}")
            height -= 25
        p.showPage()
        p.save()
        return response