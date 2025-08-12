from django.contrib import admin
from .models import (
    IngredientCategory,
    Ingredient,
    IngredientAlias,
    IngredientSource,
    Recipe,
    RecipeIngredient,
    )

class IngredientAliasInline(admin.TabularInline):
    model = IngredientAlias
    extra = 0

@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "owner", "protein_g", "carbs_g", "fat_g", "kcal")
    list_filter = ("category", "owner")
    search_fields = ("name", "barcode", "aliases__alias")
    inlines = [IngredientAliasInline]

@admin.register(IngredientSource)
class IngredientSourceAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "source", "external_id", "last_synced_at")
    list_filter = ("source",)
    search_fields = ("ingredient__name", "external_id")

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "owner", "default_portion_grams")
    list_filter = ("kind", "owner")
    search_fields = ("name",)
    inlines = [RecipeIngredientInline]