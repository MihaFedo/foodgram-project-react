from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import validate_slug

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(
        max_length=200,
        validators=[validate_slug],
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:20]


class Measurement(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name[:20]


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
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
        return self.name[:20]


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта',
    )
    name = models.CharField(max_length=200)
    text = models.TextField(
        'Описание рецепта',
        help_text='Введите описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2880)],
        verbose_name='Время приготовления в мин',
        help_text='Введите время приготовления в мин',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:20]


class IngredientRecipe(models.Model):
    '''Промежуточная модель для связи MtoM в модели Recipe'''
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        related_name='ingredient_in_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_ingredient'
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
    '''Промежуточная модель для связи MtoM в модели Recipe'''
    tag = models.ForeignKey(
        Tag,
        on_delete=models.RESTRICT,
        related_name='tag_tagrecipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tagrecipe',
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
