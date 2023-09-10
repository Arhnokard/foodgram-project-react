from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Название')
    color = models.CharField(
        max_length=7, unique=True, verbose_name='Цвет в HEX',
        validators=[
            RegexValidator(regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            message='Цвет должен быть в формате HEX')
        ],
    )
    slug = models.SlugField(max_length=200, unique=True,
                            verbose_name='Уникальный слаг')

    class Meta:
        ordering = ['name']
        verbose_name = ('Тэг')
        verbose_name_plural = ('Тэги')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единицы измерения')

    class Meta:
        ordering = ['name']
        verbose_name = ('Ингредиент')
        verbose_name_plural = ('Ингредиенты')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, db_index=True,
                            verbose_name='Название')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор',
    )
    tags = models.ManyToManyField(Tag, related_name='recipes_tag',
                                  verbose_name='Тэги')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientinRecipe',
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиенты в рецепте',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)',
    )
    image = models.ImageField(upload_to='image/', verbose_name='Картинка')

    class Meta:
        ordering = ['-id']
        verbose_name = ('Рецепт')
        verbose_name_plural = ('Рецепты')

    def __str__(self):
        return self.name


class IngredientinRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients_in_recipe', verbose_name='Cвязанные рецепты'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_with_ingredient',
        verbose_name='Связанные ингредиенты',
    )
    amount = models.IntegerField(validators=[MinValueValidator(1)],
                                 verbose_name='Количество ингредиента')

    class Meta:
        ordering = ['recipe']
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient', ),
                name='unique_ingredient'),
        ]
        verbose_name = ('Ингредиент')
        verbose_name_plural = ('Ингредиенты в рецептах')

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorite_recipes', verbose_name='Пользователь'
    )
    favorite_recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='users_favorite', verbose_name='Избранный рецепт',
    )

    class Meta:
        verbose_name = ('Избранный рецепт')
        verbose_name_plural = ('Избранные рецепты')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'favorite_recipe'], name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} -> {self.favorite_recipe}'


class Shopping(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_list', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='users_shopping_list', verbose_name='Рецепт к покупке'
    )

    class Meta:
        verbose_name = ('Рецепт к покупке')
        verbose_name_plural = ('Рецепты к покупке')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping')
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
