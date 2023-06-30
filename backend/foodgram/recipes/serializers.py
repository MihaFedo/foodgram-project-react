import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    '''Получение списка тегов или отдельного тега'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Получение списка ингредиентов или отдельного ингредиента'''
    measurement_unit = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class GetIngredientRecipeSerializer(serializers.ModelSerializer):
    '''Описание ингредиентов при выводе инфо о рецепте/рецептах'''
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        read_only=True
    )
    name = serializers.StringRelatedField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    '''Описание ингредиентов при создании рецепта'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    recipe = serializers.HiddenField(default=None)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount', 'recipe')


class Base64ImageField(serializers.ImageField):
    '''Кастомный тип поля для декодирования строки в
    файл изображения на сервере.
    '''
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AddRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания нового рецепта'''
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time', 'author'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author'),
                message='У Вас может быть только один рецепт с таким названием'
            ),
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('text', 'author'),
                message='У Вас уже есть рецепт с таким описанием'
            ),
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('image', 'author'),
                message='У Вас уже есть рецепт с таким изображением'
            )
        ]

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'В рецепте обязательно должны быть ингредиенты.'
            )
        value_id_set = set(
            value[_].get('ingredient') for _ in range(len(value))
        )
        if len(value) != len(value_id_set):
            raise serializers.ValidationError(
                'В рецепте ингредиенты не должны повторяться.'
            )
        return value

    def create_objects_tagrecipe(self, recipe, tags):
        for tag in tags:
            TagRecipe.objects.create(
                tag=tag,
                recipe=recipe,
            )

    def create_objects_ingredientrecipe(self, recipe, ingredients):
        for element in ingredients:
            IngredientRecipe.objects.create(
                ingredient=element.get('ingredient'),
                recipe=recipe,
                amount=element.get('amount'),
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_objects_tagrecipe(recipe, tags)
        self.create_objects_ingredientrecipe(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        IngredientRecipe.objects.filter(recipe=instance).delete()
        TagRecipe.objects.filter(recipe=instance).delete()

        self.create_objects_tagrecipe(instance, tags)
        self.create_objects_ingredientrecipe(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return GetRecipeSerializer(instance, context=context).data


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения расширенной информации о рецепте."""
    tags = TagSerializer(
        read_only=True,
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = GetIngredientRecipeSerializer(
        read_only=True,
        many=True,
        source='recipe_in_ingredient'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.favorited.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.in_shopping_cart.filter(user=user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    '''Сериализатор для добавления/удаления рецепта в избранное'''
    class Meta:
        model = Favorite
        fields = ('recipe', 'user',)

    def validate_recipe(self, value):
        request_method = self.context['request'].method
        curr_user = self.context['request'].user
        if (
            self.Meta.model.objects.filter(
                recipe=value,
                user=curr_user
            ).exists()
            and request_method == 'POST'
        ):
            raise serializers.ValidationError(
                {'errors': 'Этот рецепт уже был добавлен.'}
            )
        return value

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return GetRecipeShortSerializer(
            instance.recipe,
            context=context
        ).data


class GetRecipeShortSerializer(serializers.ModelSerializer):
    '''Сериализатор для вывода сокращенной информации о рецепте.'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(FavoriteSerializer):
    '''Сериализатор для добавления/удаления рецепта в список покупок'''
    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user',)
