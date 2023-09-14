from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from recipes.models import (Favorite, Ingredient, IngredientinRecipe, Recipe,
                            Shopping, Tag)
from users.models import Follow, User


class RecipeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = fields


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = fields


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id', queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientinRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, following=obj).exists()
        return False

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSubscription(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipe.count')

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = fields


    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeMiniSerializer(recipes, many=True).data


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredients_in_recipe')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 
            'name', 'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient['ingredient']['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальны')
            ingredients_list.append(ingredient['ingredient']['id'])
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        ingredient_list = []
        for data in ingredients:
            ingredient_list.append(
                IngredientinRecipe(ingredient=data['ingredient']['id'],
                                   recipe=recipe, amount=data['amount'])
            )
        IngredientinRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_in_recipe')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_in_recipe')
        recipe = super().update(instance, validated_data)
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        self.create_ingredients(ingredients, recipe)
        return instance


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True, source='ingredients_in_recipe')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(
                user=user, favorite_recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Shopping.objects.filter(
                user=user, recipe=obj).exists()
        return False


class ShoppingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shopping
        fields = ('user', 'recipe')
        read_only_fields = fields


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'favorite_recipe')
        read_only_fields = fields
