from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IngredientCategoryViewSet, IngredientViewSet, IngredientAliasViewSet,
    IngredientSourceViewSet, RecipeViewSet, RecipeIngredientViewSet
)

router = DefaultRouter()
router.register(r"categories", IngredientCategoryViewSet, basename="ingredientcategory")
router.register(r"ingredients", IngredientViewSet, basename="ingredient")
router.register(r"aliases", IngredientAliasViewSet, basename="ingredientalias")
router.register(r"sources", IngredientSourceViewSet, basename="ingredientsource")
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"recipe-ingredients", RecipeIngredientViewSet, basename="recipeingredient")

urlpatterns = [
    path("", include(router.urls)),
    ]
