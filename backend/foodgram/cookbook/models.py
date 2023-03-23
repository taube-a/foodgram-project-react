from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


User = get_user_model()

class Tag(models.Model):
    """Tag model."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Код цвета',
        unique=True,
        max_length=7,
    )
    slug = models.SlugField(
        verbose_name='Адрес', 
        unique=True)
    
    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Ingridient model."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Recipe model."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        blank=True,
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите текстовое описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингридиенты',
        help_text='Укажите ингридиенты для приготовления',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Категория',
        help_text='Укажите категорию рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(
            MinValueValidator(1, message=("Минимальное время - 1 минута"),),
        ),
        default=1,
        help_text='Укажите время приготовления (в минутах)',
    )
    
    class Meta:
        verbose_name = 'рецепт',
        verbose_name_plural = 'рецепты'
        constraints = (
            models.CheckConstraint(
                check=models.Q(cooking_time__gte=1),
                name='recipe_cooking_time_range'),
            )

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Model for connect tables Recipe and Ingredient."""
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Ингридиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(1, message='Минимальное количество - 1'),
        ),
        default=1,
    )

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

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class Follow(models.Model):
    """Following model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'подписк'
        verbose_name_plural = 'подписки'
        constraints = [models.UniqueConstraint(fields=('user', 'author'),
                                               name='unique_follow')]


class Favourite(models.Model):
    """User's favourite recipe model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='recipe is favourite',
            ),
        )

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """ShoppingCart model."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], 
                name='unique shopping chart'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
