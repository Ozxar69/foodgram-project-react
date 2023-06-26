from django.db import models


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name= 'Название тега',
        help_text= 'Название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name= 'Цвет тега',
        help_text= 'Цвет тега',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name= 'Номер тега',
        help_text= 'Номер тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
