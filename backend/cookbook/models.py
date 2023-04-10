from colorfield.fields import ColorField
from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Tag model."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
        help_text='Введите название тега.', )
    color = ColorField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=[
            validators.RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введите корретный код цвета в формате HEX.', ),
        ],
        error_messages={'unique': 'Данный цвет уже существует.'
                                  'Выберите другой.'},
        help_text='Введите код цвета в формате HEX.'
                  'Образец: #XXXXXX, где XXXXXX - код.', )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
        max_length=200,
        validators=[validators.validate_slug],
        help_text='Введите адрес для тега.'
                  'Допускаются только латиница цифры, знаки подчёркивания,'
                  ' дефисы.', )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingridient model."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=False,
        help_text='Введите название ингридиента.', )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        unique=False,
        help_text='Введите единицу измерения ингридиента.', )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique ingredient'
            )
        ]
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Recipe model."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes', )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        help_text='Введите название рецепта.', )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/', )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите текстовое описание рецепта.', )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингридиенты',
        help_text='Укажите ингридиенты для приготовления', )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Укажите категорию рецепта', )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(
            MinValueValidator(1, message=('Минимальное время - 1 минута'),),
        ),
        default=1,
        help_text='Укажите время приготовления (в минутах)', )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False, )

    class Meta:
        verbose_name = 'рецепт',
        verbose_name_plural = 'рецепты'
        constraints = (
            models.CheckConstraint(
                check=models.Q(cooking_time__gte=1),
                name='recipe_cooking_time_range'), )
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Model for connect tables Recipe and Ingredient.
    Show how many Ingredient's unit in a Recipe.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list', )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Ингридиент', )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(1, message='Минимальное количество - 1'),
        ),
        default=1, )

    class Meta:
        verbose_name = 'количество ингридиента'
        verbose_name_plural = 'количество ингридиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique ingredients recipe',
            ),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='ingredientamount_amount_range'),
        ]
        ordering = ('-id',)

    def __str__(self):
        return (f'{self.ingredient} {self.amount}'
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """User's favorite recipe model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user',),
                name='unique_user_recipe',
            ),
        )

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """ShoppingCart model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts', )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts', )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_chart', )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
