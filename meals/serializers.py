from django.db import models
from rest_framework import serializers
from .models import DayPlan, Meal, MealItem, MealItemIngredient
from .utils import calc_recipe_macros

class DayPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayPlan
        fields = "__all__"
        read_only_fields = ("protein_total_g", "carbs_total_g", "fat_total_g", "kcal_total")

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = "__all__"

class MealItemIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealItemIngredient
        fields = "__all__"

class MealItemSerializer(serializers.ModelSerializer):
    protein_g = serializers.FloatField(read_only=True)
    carbs_g   = serializers.FloatField(read_only=True)
    fat_g     = serializers.FloatField(read_only=True)
    kcal      = serializers.FloatField(read_only=True)

    class Meta:
        model = MealItem
        fields = "__all__"

    def _recalc_day_totals(self, day_plan):
        agg = MealItem.objects.filter(meal__day_plan=day_plan).aggregate(
            p=models.Sum("protein_g"), c=models.Sum("carbs_g"),
            f=models.Sum("fat_g"), k=models.Sum("kcal")
        )
        day_plan.protein_total_g = round(agg["p"] or 0, 2)
        day_plan.carbs_total_g   = round(agg["c"] or 0, 2)
        day_plan.fat_total_g     = round(agg["f"] or 0, 2)
        day_plan.kcal_total      = round(agg["k"] or 0, 2)
        day_plan.save(update_fields=["protein_total_g","carbs_total_g","fat_total_g","kcal_total","updated_at"])

    def _fill_macros(self, instance_or_data, recipe, portions):
        p, c, f, k = calc_recipe_macros(recipe, portions)
        instance_or_data["protein_g"] = p
        instance_or_data["carbs_g"]   = c
        instance_or_data["fat_g"]     = f
        instance_or_data["kcal"]      = k

    def create(self, validated_data):
        recipe  = validated_data["recipe"]
        portions = validated_data.get("portions", 1.0)
        
        self._fill_macros(validated_data, recipe, portions)
        item = super().create(validated_data)
        
        self._recalc_day_totals(item.meal.day_plan)
        return item

    def update(self, instance, validated_data):
        recipe   = validated_data.get("recipe", instance.recipe)
        portions = validated_data.get("portions", instance.portions)
        
        tmp = {}
        self._fill_macros(tmp, recipe, portions)
        for k in ["protein_g", "carbs_g", "fat_g", "kcal"]:
            validated_data[k] = tmp[k]
        item = super().update(instance, validated_data)
        
        self._recalc_day_totals(item.meal.day_plan)
        return item
