from django_filters import (CharFilter, FilterSet, ModelMultipleChoiceFilter,
                            NumberFilter)

from .models import Ingredient, Recipe, Tag


class IngredientFilterBackend(FilterSet):
    '''Фильтр ингредиентов по первым буквам в форме создания рецепта.'''
    name = CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name', ]


class RecipeFilterBackend(FilterSet):
    '''Фильтр рецептов по id автора, тегам, избранному, списку покупок.'''
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        curr_user = self.request.user.pk
        if value == 1 or value is True:
            return queryset.filter(favorited__user=curr_user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        curr_user = self.request.user.pk
        if value == 1 or value is True:
            return queryset.filter(in_shopping_cart__user=curr_user)
        return queryset
