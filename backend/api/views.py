import pdfkit
from django.contrib import messages
from django.db.models import Sum
from django.db.models.query_utils import Q
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from djoser import views
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FollowSerializer, IngredientSerializer,
                             RecipeListSerializer, RecipeSerializer,
                             RecipeShortSerializer, TagSerializer,
                             UserWithRecipesSerializer)
from cookbook.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                             ShoppingCart, Tag)
from users.models import Follow, User


class TokenCreateView(views.TokenCreateView):
    def _action(self, serializer):
        response = super()._action(serializer)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED
        return response


class UserWithRecipesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserWithRecipesSerializer
    permission_classes = (IsAuthenticated,)

    def get_author(self) -> User:
        return get_object_or_404(User, id=self.kwargs.get('author_id'))

    def get_object(self):
        return get_object_or_404(
            Follow, user=self.request.user, author=self.get_author()
        )

    def destroy(self, request, *args, **kwargs):
        self.get_author()
        try:
            self.get_object()
        except Http404:
            data = {'errors': 'Вы не подписаны на данного пользователя.'}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in (
            'create',
            'destroy',
        ):
            return FollowSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(follows__user=self.request.user)
        return None

    def perform_create(self, serializer):
        serializer.save(author=self.get_author())


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            qs_starts = queryset.filter(name__istartswith=name)
            qs_contains = queryset.filter(
                ~Q(name__istartswith=name) & Q(name__icontains=name)
            )
            queryset = list(qs_starts) + list(qs_contains)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer
    edit_serializer_class = RecipeSerializer
    edit_permission_classes = (IsAuthorOrReadOnly,)

    @staticmethod
    def generate_shopping_cart_pdf(queryset, user):
        data = {
            'page_objects': queryset,
            'user': user,
            'created': timezone.now(),
        }

        template = get_template('shopping_cart.html')
        html = template.render(data)
        pdf = pdfkit.from_string(html, False, options={'encoding': 'UTF-8'})

        filename = 'shopping_cart.pdf'
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def get_permissions(self):
        if self.action in (
            'destroy',
            'partial_update',
        ):
            return [
                permission() for permission in self.edit_permission_classes]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in (
            'create',
            'partial_update',
        ):
            return self.edit_serializer_class
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            recipes_id = (
                Favorite.objects.filter(user=user).values('recipe__id')
                if user.is_authenticated
                else []
            )
            condition = Q(id__in=recipes_id)
            queryset = queryset.filter(
                condition if is_favorited == '1' else ~condition
            ).all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', )
        if is_in_shopping_cart:
            recipes_id = (
                ShoppingCart.objects.filter(user=user).values('recipe__id')
                if user.is_authenticated
                else []
            )
            condition = Q(id__in=recipes_id)
            queryset = queryset.filter(
                condition if is_in_shopping_cart == '1' else ~condition
            ).all()
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author__id=author_id).all()
        tags = self.request.query_params.getlist('tags')
        if tags:
            tags = Tag.objects.filter(slug__in=tags).all()
            recipes_id = (
                (Tag.objects
                 .filter(tag__in=tags)
                 .values('recipe__id')
                 .distinct()))
            queryset = queryset.filter(id__in=recipes_id)
        return queryset

    @action(permission_classes=((IsAuthenticated,)), detail=False)
    def download_shopping_cart(self, request):
        queryset = (
            IngredientAmount.objects.filter(
                recipe__shoppingcartrecipe__user=request.user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(Sum('amount'))
            .order_by('ingredient__name')
        )
        return RecipeViewSet.generate_shopping_cart_pdf(
            queryset,
            request.user, )

    @staticmethod
    def create_related_object(request, pk, model, serializer, error):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(recipe=recipe, user=request.user).exists():
            return Response({'errors': error}, status.HTTP_400_BAD_REQUEST)
        instance = model(recipe=recipe, user=request.user)
        instance.save()
        serializer = serializer(
            get_object_or_404(Recipe, id=pk), context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_related_object(request, pk, model):
        get_object_or_404(model, recipe_id=pk, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk):
        return RecipeViewSet.create_related_object(
            request,
            pk,
            Favorite,
            RecipeShortSerializer,
            'Рецепт уже есть в избранном.',
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return RecipeViewSet.delete_related_object(request, pk, Favorite)

    @action(methods=['post'], detail=True)
    def shopping_cart(self, request, pk):
        return RecipeViewSet.create_related_object(
            request,
            pk,
            ShoppingCart,
            RecipeShortSerializer,
            'Рецепт уже есть в корзине.',
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return RecipeViewSet.delete_related_object(request, pk, ShoppingCart)


def upload_csv(request):
    data = {}
    if "GET" == request.method:
        return render(request, 'api/upload.html', data)
    try:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Пожалуйста, загрузите CSV-файл')
            return HttpResponseRedirect(reverse('api:upload_csv'))
        if csv_file.multiple_chunks():
            messages.error(request,
                           'Слишком большой файл (%.2f MB).'
                           % (csv_file.size / (1000 * 1000),))
            return HttpResponseRedirect(reverse('api:upload_csv'))
        file_data = csv_file.read().decode("utf-8")
        lines = file_data.split('\n')
        for line in lines:
            fields = line.split(",")
            try:
                ingredient = Ingredient(
                    name=fields[0],
                    measurement_unit=fields[1], )
                ingredient.save()
            except Exception as e:
                messages.error(request, 'Невозможно загрузить файл: '
                               + repr(e))
                pass
    except Exception as e:
        messages.error(request, 'Невозможно загрузить файл: ' + repr(e))
    return HttpResponseRedirect(reverse("api:upload_csv"))
