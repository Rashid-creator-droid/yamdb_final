from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from users.models import User


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=256)
    slug = models.SlugField('Ссылка', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Категория', max_length=256)
    slug = models.SlugField('Ссылка', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Произведение', max_length=256)
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        through='TitleGenre',
    )
    year = models.IntegerField(
        'Дата релиза',
    )
    description = models.TextField(
        'Описание произведения',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-year']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=None)
        now = timezone.now().year
        if self.year > now:
            raise ValidationError(f'Год релиза не может быть больше {now}')

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.SET_NULL,
        null=True,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'Жанры произведения'
        verbose_name_plural = 'Жанры произведения'

    def __str__(self):
        return f'Произведение:"{self.title}". Жанр:{self.genre}'


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Допустимые значние 1-10'),
            MaxValueValidator(10, message='Допустимые значние 1-10'),

        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review',
            ),
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
