from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'

    email = models.EmailField(verbose_name='Email', unique=True)
    first_name = models.CharField(verbose_name='Имя', max_length=150)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Подписан на пользователя'
    )

    class Meta:
        verbose_name = ('Подписка')
        verbose_name_plural = ('Подписки')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follow'),
            models.UniqueConstraint(
                fields=['user', 'user'], name='no_foollow_author'
            )
        ]
