from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_slug

User = get_user_model()


class Tag(models.Model):
    '''Модель тэгов (#завтрак, #обед и пр.) для рецептов.'''
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование тэга',
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет для отображения тэга',
    )
    slug = models.SlugField(
        max_length=200,
        validators=[validate_slug],
        unique=True,
        verbose_name='slug',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:20]


class Measurement(models.Model):
    '''Модель для единиц измерения ингредиентов.'''
    name = models.CharField(
        max_length=200,
        verbose_name='Ед.измерения ингредиента',
    )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name[:20]


class Ingredient(models.Model):
    '''Модель ингредиентов для составления рецептов.'''
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование ингредиента',
    )
    measurement_unit = models.ForeignKey(
        Measurement,
        on_delete=models.RESTRICT,
        related_name='ingredients',
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:25]


class Recipe(models.Model):
    '''Модель рецептов.'''
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэги рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование рецепта',
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Введите описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2880)],
        verbose_name='Время приготовления в мин',
        help_text='Введите время приготовления в мин',
    )
    date_created = models.DateTimeField(
        'Время создания',
        auto_now_add=True
    )
    last_updated = models.DateTimeField(
        'Время обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:20]


class IngredientRecipe(models.Model):
    '''Промежуточная модель для связи MtoM для Recipe и Ingredient.'''
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент в составе рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_ingredient',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Кол-во ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='model_IngredientRecipe_constraints'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} - {self.amount} - {self.recipe}'


class TagRecipe(models.Model):
    '''Промежуточная модель для связи MtoM для Recipe и Tag.'''
    tag = models.ForeignKey(
        Tag,
        on_delete=models.RESTRICT,
        related_name='tag_tagrecipe',
        verbose_name='Тэг рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tagrecipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Тэги в рецепте'
        verbose_name_plural = 'Тэги в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='model_TagRecipe_constraints'
            )
        ]

    def __str__(self):
        return f'{self.tag} - {self.recipe}'


class ShoppingCart(models.Model):
    '''Модель для рецептов в корзине покупок.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name='Покупатель',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт, добавленный в корзину',
    )

    class Meta:
        verbose_name = 'Рецепты в корзине'
        verbose_name_plural = 'Рецепты в корзинах'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='model_ShoppingCart_constraints'
            )
        ]


class Favorite(models.Model):
    '''Модель для рецептов, добавленных пользователем себе в избранное.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='elector',
        verbose_name='Пользователь, кот-й добавил рецепт в избранное',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name='Рецепт, добавленный в избранное',
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='model_Favorite_constraints'
            )
        ]
