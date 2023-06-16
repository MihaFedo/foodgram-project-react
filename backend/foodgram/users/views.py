from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .serializers import AddFollowSerializer, GetFollowSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    '''Обработка запросов при работе с пользователями и подписками.'''
    @action(["get",], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
    
    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def subscribe(self, request, id):
        try:
            get_object_or_404(User, pk=id)
        except:
            raise ValidationError(
                {'errors': 'Такого автора не существует'}
            )
        if self.request.method == 'POST':
            serializer = AddFollowSerializer(
                    data={
                        'user': self.request.user.id,
                        'author': id,
                    },
                    context={'request': self.request}
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if AddFollowSerializer.Meta.model.objects.filter(author=id).exists():
            AddFollowSerializer.Meta.model.objects.filter(author=id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого автора'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(
        methods=['get',],
        detail=False,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = GetFollowSerializer(
            page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
