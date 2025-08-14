from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, IngredientPriceViewSet

router = DefaultRouter()
router.register(r"inventory", InventoryItemViewSet, basename="inventoryitem")
router.register(r"prices", IngredientPriceViewSet, basename="ingredientprice")

urlpatterns = [path("", include(router.urls))]
