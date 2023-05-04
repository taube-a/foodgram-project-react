# Generated by Django 4.2 on 2023-05-03 09:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cookbook", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="carts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                help_text="Укажите ингридиенты для приготовления",
                related_name="recipes",
                through="cookbook.IngredientAmount",
                to="cookbook.ingredient",
                verbose_name="Ингридиенты",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                help_text="Укажите категорию рецепта",
                related_name="recipes",
                to="cookbook.tag",
                verbose_name="Теги",
            ),
        ),
        migrations.AddField(
            model_name="ingredientamount",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cookbook.ingredient",
                verbose_name="Ингридиент",
            ),
        ),
        migrations.AddField(
            model_name="ingredientamount",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredient_list",
                to="cookbook.recipe",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to="cookbook.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddConstraint(
            model_name="shoppingcart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_chart"
            ),
        ),
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.CheckConstraint(
                check=models.Q(("cooking_time__gte", 1)),
                name="recipe_cooking_time_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="ingredientamount",
            constraint=models.UniqueConstraint(
                fields=("ingredient", "recipe"), name="unique ingredients recipe"
            ),
        ),
        migrations.AddConstraint(
            model_name="ingredientamount",
            constraint=models.CheckConstraint(
                check=models.Q(("amount__gte", 1)), name="ingredientamount_amount_range"
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("recipe", "user"), name="unique_user_recipe"
            ),
        ),
    ]
