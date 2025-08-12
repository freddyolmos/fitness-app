from rest_framework import viewsets, permissions, filters
from django.db.models import Q
from .models import (
    IngredientCategory, Ingredient, IngredientAlias,
    IngredientSource, Recipe, RecipeIngredient
)
from .serializers import (
    IngredientCategorySerializer, IngredientSerializer, IngredientAliasSerializer,
    IngredientSourceSerializer, RecipeSerializer, RecipeIngredientSerializer
)

class IsAuthenticatedOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    pass

class IngredientCategoryViewSet(viewsets.ModelViewSet):
    queryset = IngredientCategory.objects.all().order_by("name")
    serializer_class = IngredientCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "barcode", "aliases__alias"]
    ordering_fields = ["name", "kcal", "protein_g", "carbs_g", "fat_g"]

    def get_queryset(self):
        user = self.request.user
        return Ingredient.objects.select_related("category", "owner")\
            .filter(Q(owner=user) | Q(owner__isnull=True))\
            .order_by("name")\
            .distinct()

    def perform_create(self, serializer):
        owner = serializer.validated_data.get("owner") or self.request.user
        serializer.save(owner=owner)

class IngredientAliasViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientAliasSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return IngredientAlias.objects.filter(
            Q(ingredient__owner=user) | Q(ingredient__owner__isnull=True)
        ).select_related("ingredient")

class IngredientSourceViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return IngredientSource.objects.filter(
            Q(ingredient__owner=user) | Q(ingredient__owner__isnull=True)
        ).select_related("ingredient")

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "default_portion_grams"]

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.select_related("owner").filter(
            Q(owner=user) | Q(owner__isnull=True)
        ).order_by("name")

    def perform_create(self, serializer):
        owner = serializer.validated_data.get("owner") or self.request.user
        serializer.save(owner=owner)

class RecipeIngredientViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeIngredientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return RecipeIngredient.objects.select_related("recipe", "ingredient").filter(
            Q(recipe__owner=user) | Q(recipe__owner__isnull=True)
        )