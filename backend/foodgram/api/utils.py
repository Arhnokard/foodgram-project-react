from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def create_shopping_cart(ingredients):
    shopping_list = 'Купить в магазине:'
    for ingredient in ingredients:
        shopping_list += (
            f"\n{ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']}) - "
            f"{ingredient['amount']}")
    file = 'shopping_list.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
    return response


def joint_post(user, pk, model, serializer):
    if not model.objects.filter(user=user, recipe_id=pk).exists():
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        obj_serializer = serializer(recipe)
        return Response(data=obj_serializer.data,
                        status=status.HTTP_201_CREATED)
    return Response('Рецепт уже добавлен', status=status.HTTP_400_BAD_REQUEST)


def joint_delete(user, pk, model):
    post = model.objects.filter(user=user, recipe__id=pk)
    if post.exists():
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response('Рецепт уже удален', status=status.HTTP_400_BAD_REQUEST)
