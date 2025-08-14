from django.db import models, transaction
from rest_framework import serializers
from .models import DayPlan, Meal, MealItem, MealItemIngredient
from .utils import calc_recipe_macros, recalc_meal_item_and_day
from nutrition.models import RecipeIngredient

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

    @transaction.atomic
    def create(self, validated_data):
        meal = validated_data["meal"]
        recipe  = validated_data["recipe"]
        portions = validated_data.get("portions", 1.0)

        item = super().create(validated_data)

        ris = RecipeIngredient.objects.select_related("ingredient").filter(recipe=recipe)
        bulk = []
        for ri in ris:
            bulk.append(MealItemIngredient(
                meal_item=item,
                ingredient=ri.ingredient,
                amount=ri.amount * portions,
                unit=ri.unit
            ))
        if bulk:
            MealItemIngredient.objects.bulk_create(bulk)

        recalc_meal_item_and_day(item)
        return item

    @transaction.atomic
    def update(self, instance, validated_data):
        new_portions = validated_data.get("portions", instance.portions)
        if "portions" in validated_data and new_portions != instance.portions:
            factor = new_portions / instance.portions if instance.portions else 1.0
            for mii in instance.ingredients.all():
                mii.amount = round(mii.amount * factor, 4)
                mii.save(update_fields=["amount","updated_at"])
        item = super().update(instance, validated_data)
        recalc_meal_item_and_day(item)
        return item