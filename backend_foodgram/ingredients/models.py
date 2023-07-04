from django.db import models


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(
        max_length=255,
        verbose_name='Название ингредиента',
        help_text='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единица измерения',
        help_text='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Ингридиентов'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'
