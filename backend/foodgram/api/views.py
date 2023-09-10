from django.http import HttpResponse
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
                             RecipeMiniSerializer, RecipeSerializer,
                             TagSerializer, UserSubscription)
from recipes.models import (Favorite, Ingredient, IngredientinRecipe, Recipe,
                            Shopping, Tag)
from users.models import Follow, User


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
        response_data = {
            'count': subs.count(),
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
            'results': serializer.data}
        return Response(response_data)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = self.request.user
        following = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if user != following and not Follow.objects.filter(
                    user=user, following=following).exists():
                follow = Follow.objects.create(user=user, following=following)
                serializer = UserSubscription(
                    following, context={'request': request})
                return Response(
                    data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow = get_object_or_404(Follow, user=user, following=following)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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
        user = self.request.user
        ingredients = IngredientinRecipe.objects.filter(
            recipe__users_shopping_list__user=user).values(
                'ingredient__name', 'ingredient__measurement_unit', 'amount')
        ingredients_data = {}
        for ing in ingredients:
            name_unit = (f"{ing['ingredient__name']} "
                         f"({ing['ingredient__measurement_unit']})")
            amount = ing['amount']
            if name_unit in ingredients_data:
                ingredients_data[name_unit] += amount
            else:
                ingredients_data[name_unit] = amount
        ingredient_list = "Cписок покупок:\n"
        for name, amount in ingredients_data.items():
            ingredient_list += f'\n{name} -> {amount}'
        file = 'shopping-list.txt'
        response = HttpResponse(
            ingredient_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response
