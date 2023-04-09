from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models
from rest_framework.exceptions import ValidationError

from .validators import validate_username

LIMIT_NOTIFICATION = ('Только буквы, цифры и @/./+/-/_'
                      'Длина не должна превышать 256 символов')


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )

    username = models.CharField(
        'Логин',
        max_length=256,
        unique=True,
        blank=False,
        null=False,
        help_text=LIMIT_NOTIFICATION,
        error_messages={'unique': 'Пользователь с таким именем'
                                  'уже существует.', },
        validators=[validate_username, ASCIIUsernameValidator], )
    first_name = models.CharField(
        'Имя',
        max_length=256,
        blank=False,
        null=False,
        help_text=LIMIT_NOTIFICATION, )
    last_name = models.CharField(
        'Фамилия',
        max_length=256,
        blank=False,
        null=False,
        help_text=LIMIT_NOTIFICATION, )
    email = models.EmailField(
        'Электронная почта',
        max_length=256,
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует.',
        },
        help_text=LIMIT_NOTIFICATION, )
    password = models.CharField(
        'Пароль',
        max_length=256,
        help_text=LIMIT_NOTIFICATION,
        blank=False,
        null=False, )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    def save(self, **kwargs):
        if self.user == self.author:
            raise ValidationError('Подписка на себя невозможна.')
        super().save()

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
