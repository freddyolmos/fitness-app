from rest_framework import viewsets, permissions, filters
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import DayPlan, Meal, MealItem, MealItemIngredient
from .serializers import (
    DayPlanSerializer, MealSerializer, MealItemSerializer, MealItemIngredientSerializer
)

class IsAuthenticated(permissions.IsAuthenticated):
    pass

class DayPlanViewSet(viewsets.ModelViewSet):
    serializer_class = DayPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["date", "created_at"]

    def get_queryset(self):
        return DayPlan.objects.filter(user=self.request.user).order_by("-date")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MealViewSet(viewsets.ModelViewSet):
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Meal.objects.select_related("day_plan").filter(day_plan__user=self.request.user)

    def perform_create(self, serializer):
        day_plan = serializer.validated_data["day_plan"]
        if day_plan.user != self.request.user:
            raise permissions.PermissionDenied("DayPlan no pertenece al usuario autenticado.")
        serializer.save()

class MealItemViewSet(viewsets.ModelViewSet):
    serializer_class = MealItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealItem.objects.select_related("meal", "meal__day_plan", "recipe")\
            .filter(meal__day_plan__user=self.request.user)

    def perform_create(self, serializer):
        meal = serializer.validated_data["meal"]
        if meal.day_plan.user != self.request.user:
            raise permissions.PermissionDenied("Meal no pertenece al usuario autenticado.")
        serializer.save()

class MealItemIngredientViewSet(viewsets.ModelViewSet):
    serializer_class = MealItemIngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealItemIngredient.objects.select_related("meal_item", "meal_item__meal", "meal_item__meal__day_plan")\
            .filter(meal_item__meal__day_plan__user=self.request.user)
