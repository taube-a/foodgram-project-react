from cookbook.models import Ingredient, IngredientAmount, Recipe, Tag
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from users.models import Follow, User


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time', )
        read_only_fields = fields


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (tuple(User.REQUIRED_FIELDS)
                  + (User.USERNAME_FIELD, 'password', ))


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, user_obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, author=user_obj).exists()
        )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed', )


class FollowSerializer(CustomUserCreateSerializer):
    recipes_count = SerializerMethodField(read_only=True)
    recipes = SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('username', 'email',)
    
    def get_is_subscribed(self, user_obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, author=user_obj).exists()
        )

    def validate(self, data):
        user = self.context['request'].user
        author = self.instance
        if user == author:
            raise ValidationError(
                'Подписка на себя невозможна.',
                code=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                'Подписка на данного пользователя уже оформлена.',
                code=status.HTTP_400_BAD_REQUEST)
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeShortSerializer(queryset, many=True).data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='id',
        queryset=Ingredient.objects.all(), )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True, )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True, )

    class Meta:
        model = IngredientAmount
        exclude = ('recipe', 'ingredient', )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True, )
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and (user.carts.filter(recipe=recipe).exists()))
    
    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientamount__amount')
        )   


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True, )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(), )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time', )

    def to_representation(self, recipe):
        return RecipeReadSerializer(recipe, context=self.context).data

    def create_ingredient_amounts(self, recipe, ingredientamount_set):
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount'], )
            for item in ingredientamount_set]
        )

    def create(self, validated_data):
        ingredientamount_set = validated_data.pop('ingredientamount_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, )
        recipe.tags.set(tags)
        self.create_ingredient_amounts(recipe, ingredientamount_set)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredientamount_set' in validated_data:
            ingredientamount_set = validated_data.pop('ingredientamount_set')
            if ingredientamount_set:
                recipe.ingredients.clear()
            self.create_ingredient_amounts(
                recipe, ingredientamount_set
            )
        return super().update(recipe, validated_data)

    def validate(self, attrs):
        if len(attrs['tags']) == 0:
            raise serializers.ValidationError('Должен быть выбран'
                                              ' хотя бы один тег.')
        if len(attrs['tags']) != len(set(attrs['tags'])):
            raise serializers.ValidationError('Теги должны быть уникальны.')
        if len(attrs['ingredientamount_set']) == 0:
            raise serializers.ValidationError(
                'Должен быть выбран хотя бы один ингредиент.'
            )
        ingredients = attrs['ingredientamount_set']
        if (len(ingredients)
                != len(set(obj['ingredient'] for obj in ingredients))):
            raise serializers.ValidationError(
                'Такой ингридиент уже используется')
        if any(obj['amount'] <= 0 for obj in ingredients):
            raise serializers.ValidationError(
                'Количество игредиента должно быть больше нуля.')
        if attrs['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля.')
        return super().validate(attrs)
