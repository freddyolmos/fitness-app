
from rest_framework import viewsets, permissions, filters
from django.db.models import Q
from .models import InventoryItem, IngredientPrice
from .serializers import InventoryItemSerializer, IngredientPriceSerializer

class IsAuthenticated(permissions.IsAuthenticated):
    pass

class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["ingredient__name"]
    ordering_fields = ["updated_at", "last_checked_at"]

    def get_queryset(self):
        return InventoryItem.objects.select_related("ingredient","user")\
            .filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IngredientPriceViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientPriceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["ingredient__name", "store__name"]
    ordering_fields = ["observed_at", "price_per_unit"]

    def get_queryset(self):
        qs = IngredientPrice.objects.select_related("ingredient","store").all()
        ing = self.request.query_params.get("ingredient")
        store = self.request.query_params.get("store")
        if ing:
            qs = qs.filter(ingredient_id=ing)
        if store:
            qs = qs.filter(store_id=store)
        return qs