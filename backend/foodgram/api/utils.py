from django.core.exceptions import ValidationError


def len_valid(len_1, len_2):
    return len_1 != len_2


def tags_validator(tags, tag):
    if tags is None or len(tags) == 0:
        raise ValidationError('Не указаны тэги')
    len_tags_set = len(set(tags))
    if len_valid(len(tags), len_tags_set):
        raise ValidationError('В запросе повторяющиеся тэги')
    tags_obj = tag.objects.filter(id__in=tags)
    if len_valid(len_tags_set, len(tags_obj)):
        raise ValidationError('В запросе несуществующий тэг')
    return tags


def ingredients_validator(ingredients, ingredient):
    if ingredients is None or len(ingredients) == 0:
        raise ValidationError('Не указаны ингредиенты')
    ingredient_ids = [ingredient['id'] for ingredient in ingredients]
    len_ing_ids_set = len(set(ingredient_ids))
    ingredients_obj = ingredient.objects.filter(id__in=ingredient_ids)
    if len_valid(len(ingredient_ids), len_ing_ids_set):
        raise ValidationError('В запросе повторяющиеся ингредиенты')
    if len_valid(len_ing_ids_set, len(ingredients_obj)):
        raise ValidationError('В запросе несуществующие ингредиенты')
    return ingredients
