from django.contrib import admin

from .models import Tag, Recipe, Ingredient, ShoppingCart, Favourite, Follow

admin.site.register(Tag)
admin.site.register(Recipe) 
admin.site.register(Ingredient)
admin.site.register(ShoppingCart)
admin.site.register(Favourite)
admin.site.register(Follow)
