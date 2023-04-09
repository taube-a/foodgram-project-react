from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       TokenCreateView, UserWithRecipesViewSet, upload_csv)
from django.urls import include, path
from djoser.views import TokenDestroyView, UserViewSet
from rest_framework import routers

app_name = 'api'

auth_patterns = [
    path(r'token/login/', TokenCreateView.as_view(), name='login'),
    path(r'token/logout/', TokenDestroyView.as_view(), name='logout'),
]

users_patterns = [
    path(
        r'',
        UserViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='users', ),
    path(
        r'<int:id>/',
        UserViewSet.as_view({'get': 'retrieve'}),
        name='user-detail', ),
    path(
        r'me/',
        UserViewSet.as_view({'get': 'me'}),
        name='me-detail', ),
    path(
        r'set_password/',
        UserViewSet.as_view({'post': 'set_password'}),
        name='set-password',),
    path(
        r'subscriptions/',
        UserWithRecipesViewSet.as_view({'get': 'list'}),
        name='subscriptions', ),
    path(
        r'<int:author_id>/subscribe/',
        UserWithRecipesViewSet.as_view(
            {'post': 'create',
             'delete': 'destroy', }, ),
        name='subscribe', ), ]

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(r'auth/', include(auth_patterns)),
    path(r'users/', include(users_patterns)),
    path(r'', include(router.urls)),
    path('upload_csv/', upload_csv, name='upload_csv'),
]
