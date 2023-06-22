from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, IngredientRecipe, Measurement,
                     Recipe, ShoppingCart, Tag, TagRecipe)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count', 'image_tag')
    list_filter = ('author', 'name', 'tags',)
    inlines = [
        IngredientRecipeInline,
        TagRecipeInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(favorite_count=Count('favorited'))

    def favorite_count(self, obj):
        return obj.favorite_count

    def image_tag(self, obj):
        return mark_safe('<img src="{}" height="50"/>'.format(obj.image.url))


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Tag, TagAdmin)
admin.site.register(Measurement)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
