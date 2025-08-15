"""
URL configuration for nutrition_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core.views import UserProfileViewSet, StoreViewSet
from nutrition.views import (
    IngredientCategoryViewSet, IngredientViewSet, IngredientAliasViewSet,
    IngredientSourceViewSet, RecipeViewSet, RecipeIngredientViewSet,
)
from meals.views import DayPlanViewSet, MealViewSet, MealItemViewSet, MealItemIngredientViewSet
from commerce.views import InventoryItemViewSet, IngredientPriceViewSet

router = routers.DefaultRouter()

# core
router.register(r"user-profiles", UserProfileViewSet, basename="userprofile")
router.register(r"stores", StoreViewSet, basename="store")
# nutrition
router.register(r"ingredient-categories", IngredientCategoryViewSet, basename="ingredientcategory")
router.register(r"ingredients", IngredientViewSet, basename="ingredient")
router.register(r"ingredient-aliases", IngredientAliasViewSet, basename="ingredientalias")
router.register(r"ingredient-sources", IngredientSourceViewSet, basename="ingredientsource")
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"recipe-ingredients", RecipeIngredientViewSet, basename="recipeingredient")
# meals
router.register(r"day-plans", DayPlanViewSet, basename="dayplan")
router.register(r"meals", MealViewSet, basename="meal")
router.register(r"meal-items", MealItemViewSet, basename="mealitem")
router.register(r"meal-item-ingredients", MealItemIngredientViewSet, basename="mealitemingredient")
# commerce
router.register(r"inventory", InventoryItemViewSet, basename="inventory")
router.register(r"ingredient-prices", IngredientPriceViewSet, basename="ingredientprice")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("router.urls")),
    # JWT
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]