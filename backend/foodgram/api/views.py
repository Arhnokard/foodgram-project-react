from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeMiniSerializer, ReadRecipeSerializer,
                             CreateRecipeSerializer, TagSerializer,
                             UserSubscription)
from recipes.models import (Favorite, Ingredient, IngredientinRecipe, Recipe,
                            Shopping, Tag)
from users.models import Follow, User
from .utils import create_shopping_cart


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        user = self.request.user
        subs = User.objects.filter(following__user=user)
        page = self.paginate_queryset(subs)
        serializer = UserSubscription(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = self.request.user
        following = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            serializer = UserSubscription(
                following, data=request.data, context={'request': request}
            )
            if serializer.is_valid():
                Follow.objects.create(user=user, following=following)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow = get_object_or_404(Follow, user=user, following=following)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = ReadRecipeSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not Shopping.objects.filter(user=user, recipe=recipe).exists():
                shopping = Shopping.objects.create(user=user, recipe=recipe)
                serializer = RecipeMiniSerializer(
                    recipe, context={'request': request})
                return Response(
                    data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopping = get_object_or_404(Shopping, user=user, recipe=recipe)
        shopping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not Favorite.objects.filter(
                    user=user, favorite_recipe=recipe).exists():
                favorite = Favorite.objects.create(
                    user=user, favorite_recipe=recipe)
                serializer = RecipeMiniSerializer(
                    recipe, context={'request': request})
                return Response(
                    data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        favorite = get_object_or_404(
            Favorite, user=user, favorite_recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = IngredientinRecipe.objects.filter(
            recipe__users_shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return create_shopping_cart(ingredients)
