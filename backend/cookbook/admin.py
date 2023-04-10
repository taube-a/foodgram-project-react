from django.contrib import admin

from cookbook.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                             ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    list_filter = ('name', )
    search_fields = ('name', )
    ordering = ('measurement_unit', )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug', )
    search_fields = ('name', 'slug', )
    ordering = ('color', )


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 2
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'pub_date', 'name', 'text', 'cooking_time',
                    'get_tags', 'get_ingredients', 'count_favorites', )
    readonly_fields = ('count_favorites', )
    list_filter = ('name', 'tags', )
    search_fields = (
        'name', 'cooking_time',
        'author__email', 'ingredient__name')
    empty_value_display = '-пусто-'
    inlines = (IngredientAmountInline, )

    @admin.display(description='Количество в избранных')
    def count_favorites(self, obj):
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n '.join([
            f"{item['ingredient__name']} - {item['amount']}"
            f" {item['ingredient__measurement_unit']}."
            for item in obj.ingredient_list.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        """Получаем теги."""
        return (', '
                .join(tag for tag in obj.tags.values_list('name',
                                                          flat=True)))


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    empty_value_display = '-пусто-'
