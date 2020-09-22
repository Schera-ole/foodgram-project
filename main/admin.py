from django.contrib import admin
from .models import Ingredient, IngredientAmount, Favorite, Recipe


class IngredientAmount_inline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    inlines = (IngredientAmount_inline,)
    list_display = ('pk', 'title', 'dimension',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientAmount_inline,)
    search_fields = ('title',)
    list_filter = ('author', 'title', 'tags',)
    empty_value_display = '-пусто-'
    list_display = ('pk', 'author', 'title', 'tags', 'recipe_favor_count',)

    def recipe_favor_count(self, obj):
        return obj.recipe_favorite.count()

    recipe_favor_count.short_description = "Favorite Count"

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientAmount)
admin.site.register(Ingredient, IngredientAdmin)
