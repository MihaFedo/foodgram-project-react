from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import Follow
from .validators import validate_username, validate_email

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    '''Отображение информации о пользователях'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'username',
            'is_subscribed',
        )
        read_only_fields = (settings.LOGIN_FIELD,)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Создание пользователя'''
    username = serializers.SlugField(
        required=True,
        max_length=150,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Придумайте другой username, такой уже существует!'
        ), validate_username]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Укажите другой email, такой уже существует!'
        ), validate_email]
    )

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'username',
            'password',
        )


class AddFollowSerializer(serializers.ModelSerializer):
    '''Сериализатор для добавления и удаления подписки на пользователей'''
    class Meta:
        model = Follow
        fields = ('user', 'author',)
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author',),
                message='Вы уже подписаны на этого автора'
            ),
        ]

    def validate_author(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError(
                'Какой же смысл подписываться самому на себя?! Так нельзя)'
            )
        return value

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return GetFollowSerializer(instance.author, context=context).data


class GetFollowSerializer(CustomUserSerializer):
    """Сериализатор для отображения расширенной информации о подписках."""
    from recipes.serializers import GetRecipeShortSerializer
    recipes = GetRecipeShortSerializer(
        read_only=True,
        many=True,
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
