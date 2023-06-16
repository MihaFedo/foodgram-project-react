from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class ExtUser(AbstractUser):
    username = models.CharField(
        verbose_name='username',
        max_length=150,
        validators=[validate_username],
        unique=True
    )
    email = models.EmailField(
        verbose_name='email',
        unique=True,
        blank=False,
        max_length=254,
    )
    first_name = models.CharField(
        verbose_name='first_name',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='last_name',
        max_length=150,
        blank=False,
    )
    password = models.CharField('password', max_length=150)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('username',)
    
    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        ExtUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        ExtUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписались',
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='model_Follow_constraints'
            )
        ]
