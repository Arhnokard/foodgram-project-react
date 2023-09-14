from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientinRecipe, Recipe,
                            Shopping, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientinRecipeInline(admin.TabularInline):
    model = IngredientinRecipe
    min_num = 1


class RecipeFilter(admin.SimpleListFilter):
    title = 'Рецепт'
    parameter_name = 'recipe'

    def lookups(self, request, model_admin):
        recipes = set(
            IngredientinRecipe.objects.values_list(
                'recipe__id', 'recipe__name')
        )
        return recipes

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(recipe__id=self.value())


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'add_in_favorites')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author__email', 'name', 'tags__name')
    inlines = [IngredientinRecipeInline]

    def add_in_favorites(self, obj):
        return obj.users_favorite.count()

    add_in_favorites.short_description = 'Добавлен в избранное'


class IngredientinRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = (RecipeFilter,)


class FavoriteAdmin(admin.ModelAdmin):
    list_filter = ('user',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientinRecipe, IngredientinRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Shopping)
