from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint

from users.models import User
from tags.models import Tag
from ingredients.models import Ingredient


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        help_text='Автор рецепта'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название рецепта',
        help_text='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Фото рецепта',
        help_text='Фото рецепта',
        upload_to='recipes/'
    )
    description = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиенты для рецепта',
        help_text='Ингредиенты для рецепта',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        verbose_name='Теги для рецепта',
        help_text='Теги для рецепта',
        related_name='recipes'
    )
    cook_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления рецепта',
        help_text='Время приготовления рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    count = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'Ingredient'],
                name='unique_recipe_ingredients'
            )
        ]

    def __str__(self):
        return (f'{self.recipe}: {self.ingredient.name};'
                f' {self.count}, {self.ingredient.measurement_unit}')


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='favorite_recipes'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(
                fields=('user','recipe'),
                name='unique_favorite_recipes'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранных рецептах у {self.user}'


class ShoppingList(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_list',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopping_list',
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=('user','recipe'),
                name='unique_recipe_in_shopping_list'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
