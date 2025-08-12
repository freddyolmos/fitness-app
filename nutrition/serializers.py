from rest_framework import serializers
from .models import (
    IngredientCategory, Ingredient, IngredientAlias,
    IngredientSource, Recipe, RecipeIngredient
)

class IngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = "__all__"

class IngredientAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientAlias
        fields = "__all__"

class IngredientSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientSource
        fields = "__all__"

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"

    def validate(self, data):
        protein = data.get("protein_g", getattr(self.instance, "protein_g", 0) if self.instance else 0)
        carbs   = data.get("carbs_g",   getattr(self.instance, "carbs_g", 0) if self.instance else 0)
        fat     = data.get("fat_g",     getattr(self.instance, "fat_g", 0) if self.instance else 0)
        kcal    = data.get("kcal",      getattr(self.instance, "kcal", 0) if self.instance else 0)

        if (kcal is None or kcal == 0) and any([protein, carbs, fat]):
            data["kcal"] = round(protein * 4 + carbs * 4 + fat * 9, 2)
        return data

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = "__all__"

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = "__all__"