from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint

from users.models import User
from tags.models import Tag
from ingredients.models import Ingredient


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты в этом рецепте',
        through='RecipeIngredient',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    description = models.TextField(
        verbose_name='Описание рецепта',
        max_length=255,
    )
    cook_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        validators=(MinValueValidator(
            1, 'Минимальный порог приготовления 1 минута'),
        )
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    pub_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата публикации',
    )
    image = models.ImageField(
        verbose_name='Картинка к рецепту',
        upload_to='recipes/',
        blank=True,

    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name[:15]}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиентов'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_for_recipe'
            )
        ]

    def __str__(self):
        return (f'{self.recipe}: {Ingredient.name},'
                f' {self.amount}, {Ingredient.measurement_unit}')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
