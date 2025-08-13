from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DayPlanViewSet, MealViewSet, MealItemViewSet, MealItemIngredientViewSet

router = DefaultRouter()
router.register(r"day-plans", DayPlanViewSet, basename="dayplan")
router.register(r"meals", MealViewSet, basename="meal")
router.register(r"items", MealItemViewSet, basename="mealitem")
router.register(r"item-ingredients", MealItemIngredientViewSet, basename="mealitemingredient")

urlpatterns = [path("", include(router.urls))]
