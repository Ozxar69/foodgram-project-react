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
    count = models.IntegerField(
        max_length=255,
        verbose_name='Количество',
        help_text='Количество',
    )

    class Meta:
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'
