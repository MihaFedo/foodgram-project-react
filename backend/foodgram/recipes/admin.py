from django.contrib import admin
from django.db.models import Count

from .models import (
    Tag, Measurement, Ingredient, Recipe, IngredientRecipe,
    TagRecipe, ShoppingCart, Favorite
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    list_filter = ('author', 'name', 'tags',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(favorite_count = Count('favorited'))
        return qs

    def favorite_count(self, obj):
        return obj.favorite_count


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)

admin.site.register(Tag)
admin.site.register(Measurement)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
