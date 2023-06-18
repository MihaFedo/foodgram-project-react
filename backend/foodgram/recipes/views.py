from rest_framework import status, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum, Prefetch
import io
import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics

from .models import (
    Tag, Ingredient, Recipe, ShoppingCart, IngredientRecipe, TagRecipe
)
from .filters import IngredientFilterBackend, RecipeFilterBackend
from .serializers import (
    TagSerializer, IngredientSerializer, AddRecipeSerializer,
    FavoriteSerializer, ShoppingCartSerializer
)
from .exceptions import NotFoundRecipe


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Обработка запросов для получения списка тегов или отдельного тега'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Обработка запросов для получения списка/отдельного ингредиента'''
    queryset = Ingredient.objects.select_related('measurement_unit').all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_class = IngredientFilterBackend


class RecipeViewSet(viewsets.ModelViewSet):
    '''Обработка запросов при работе с рецептами'''
    queryset = Recipe.objects.select_related('author').prefetch_related(
        Prefetch(
            'recipe_in_ingredient',
            queryset=IngredientRecipe.objects.select_related('ingredient')
        ),
        Prefetch(
            'recipe_tagrecipe',
            queryset=TagRecipe.objects.select_related('tag')
        ),
    ).all()
    serializer_class = AddRecipeSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilterBackend
    ordering = ('-date_created')

    def post_del_for_shop_cart_and_favorite(
        self, request, pk, serializer, ERROR_TEXT
    ):
        '''Общий метод для обработки запросов в избранное и список покупок'''
        if not Recipe.objects.filter(pk=pk).exists():
            raise NotFoundRecipe()

        if self.request.method == 'POST':
            serializer = serializer(
                data={
                    'user': self.request.user.pk,
                    'recipe': pk,
                },
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if serializer.Meta.model.objects.filter(recipe=pk).exists():
            serializer.Meta.model.objects.filter(recipe=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': ERROR_TEXT},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def favorite(self, request, pk):
        serializer = FavoriteSerializer
        ERROR_TEXT = 'Такого рецепта нет в избранном.'
        return self.post_del_for_shop_cart_and_favorite(
            request, pk, serializer, ERROR_TEXT
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        serializer = ShoppingCartSerializer
        ERROR_TEXT = 'Такого рецепта нет в списке покупок.'
        return self.post_del_for_shop_cart_and_favorite(
            request, pk, serializer, ERROR_TEXT
        )

    @action(
        methods=['get', ],
        detail=False,
    )
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='application/pdf')
        cur_date = datetime.date.today()
        response['Content-Disposition'] = (
            f'inline; filename="Купить {cur_date}.pdf"'
        )

        user = self.request.user
        purchase_queryset = ShoppingCart.objects.filter(user=user).values_list(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit__name',
        ).annotate(sum=Sum('recipe__recipe_in_ingredient__amount'))

        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'data/DejaVuSerif.ttf'))

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        p.setFont('DejaVuSerif', 15, leading=None)
        p.setFillColorRGB(0.29296875, 0.453125, 0.609375)
        p.drawString(260, 800, 'Foodgram')
        p.line(0, 780, 1000, 780)
        p.line(0, 778, 1000, 778)
        x1 = 20
        y1 = 750

        for elem in purchase_queryset:
            p.setFont('DejaVuSerif', 12, leading=None)
            p.drawString(x1, y1 - 20, f'{elem[0]} ({elem[1]}) - {elem[2]}')
            y1 -= 20

        p.setTitle(f'Список покупок на {cur_date}')
        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response
