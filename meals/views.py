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
        day = serializer.save(user=self.request.user)
        from .models import Meal
        existing = set(Meal.objects.filter(day_plan=day).values_list("slot", flat=True))
        for slot, _label in Meal.SLOTS:
            if slot not in existing:
                Meal.objects.create(day_plan=day, slot=slot)

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
        meal_item = serializer.validated_data["meal_item"]
        if meal_item.meal.day_plan.user != self.request.user:
            raise permissions.PermissionDenied("No puedes modificar ingredientes de otro usuario.")
        instance = serializer.save()
        from .utils import recalc_meal_item_and_day
        recalc_meal_item_and_day(instance.meal_item)

    def perform_update(self, serializer):
        instance = serializer.save()
        from .utils import recalc_meal_item_and_day
        recalc_meal_item_and_day(instance.meal_item)

    def perform_destroy(self, instance):
        day = instance.meal.day_plan
        super().perform_destroy(instance)
        from django.db import models
        agg = MealItem.objects.filter(meal__day_plan=day).aggregate(
            p=models.Sum("protein_g"), c=models.Sum("carbs_g"),
            f=models.Sum("fat_g"), k=models.Sum("kcal")
        )
        day.protein_total_g = round(agg["p"] or 0, 2)
        day.carbs_total_g   = round(agg["c"] or 0, 2)
        day.fat_total_g     = round(agg["f"] or 0, 2)
        day.kcal_total      = round(agg["k"] or 0, 2)
        day.save(update_fields=["protein_total_g","carbs_total_g","fat_total_g","kcal_total","updated_at"])

class MealItemIngredientViewSet(viewsets.ModelViewSet):
    serializer_class = MealItemIngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MealItemIngredient.objects.select_related("meal_item", "meal_item__meal", "meal_item__meal__day_plan")\
            .filter(meal_item__meal__day_plan__user=self.request.user)