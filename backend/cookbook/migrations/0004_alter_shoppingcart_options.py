# Generated by Django 4.2 on 2023-05-03 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cookbook", "0003_alter_favorite_options_alter_favorite_recipe"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="shoppingcart",
            options={
                "default_related_name": "shopping_cart",
                "verbose_name": "корзина",
                "verbose_name_plural": "корзины",
            },
        ),
    ]
