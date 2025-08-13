from django.contrib import admin
from .models import (
    DayPlan,
    Meal,
    MealItem,
    MealItemIngredient,
)

class MealItemIngredientInline(admin.TabularInline):
    model = MealItemIngredient
    extra = 0

class MealItemInline(admin.TabularInline):
    model = MealItem
    extra = 0

@admin.register(DayPlan)
class DayPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "protein_total_g", "carbs_total_g", "fat_total_g", "kcal_total")
    list_filter = ("user", "date")
    search_fields = ("user__username", "user__email")

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("day_plan", "slot", "created_at")
    list_filter = ("slot",)
    inlines = [MealItemInline]

@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ("meal", "recipe", "portions", "protein_g", "carbs_g", "fat_g", "kcal")
    inlines = [MealItemIngredientInline]