import base64

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .users import UsersSerializer
from .tags import TagSerializer
from recipes.models import (
    FavoriteRecipe,
    Recipe,
    RecipeIngredient,
    ShoppingList
)
from ingredients.models import Ingredient


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для подробного описания ингредиентов в рецепте."""
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('name', 'measurement_unit', 'count', 'id')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='Ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'count')


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cook_time')


class FullRecipeInformationSerealizer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации."""
    author = UsersSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredient'
    )
    tags = TagSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_user_related_item_status',
        read_only=True,
        item_type='favorite'
    )

    is_in_shopping_list = serializers.SerializerMethodField(
        method_name='get_user_related_item_status',
        read_only=True,
        item_type='list'
    )

    class Meta:
        model = Recipe
        fields = (
            'author', 'id', 'name', 'description', 'cook_time', 'image',
            'tags', 'ingredients', 'is_favorite', 'is_in_shopping_list'
        )

    def get_user_action(self, object, item_type):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if item_type == 'favorite':
            return object.favorite.filter(user=user).exists()
        elif item_type == 'list':
            return object.shopping_cart.filter(user=user).exists()
        else:
            return False


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'description', 'cook_time')

    def validate_ingredients(self, data):
        """Валидация повторяющихся ингредиентов"""
        ingredients = [item['Ingredient'] for item in data['Ingredients']]
        duplicates = set(
            [ingr for ingr in ingredients if ingredients.count(ingr) > 1])
        if duplicates:
            raise ValidationError(
                {
                    'error': f"Следующие ингредиенты повторяются:"
                             f" {', '.join(duplicates)}. "
                             "Используйте только уникальные ингредиенты."}
            )
        return data

    def get_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                count=ingredient.get('count'),
            ) for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.get_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return FullRecipeInformationSerealizer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для перемещения рецепта в избранном."""
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def exists_validation(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен'}
            )
        return data

    def to_representation_for_recipe_info_serializer(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeInfoSerializer(instance.recipe, context=context).data


class ShoppingListSerializer(FavoriteSerializer):
    """Сериализатор для добавления или удаления в списке покупок."""
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingList
