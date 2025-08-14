from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from nutrition.models import Ingredient, Recipe
from core.models import MinValueValidator

class DayPlan(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    protein_total_g = models.FloatField(default=0)
    carbs_total_g   = models.FloatField(default=0)
    fat_total_g     = models.FloatField(default=0)
    kcal_total      = models.FloatField(default=0)
    class Meta:
        unique_together = (("user","date"),)

    def __str__(self):
        return f"{self.user} · {self.date}"

class Meal(TimeStampedModel):
    SLOTS=[("desayuno","Desayuno"),("colacion1","Colación 1"),
           ("comida","Comida"),("colacion2","Colación 2"),("cena","Cena")]
    day_plan = models.ForeignKey(DayPlan, on_delete=models.CASCADE, related_name="meals")
    slot = models.CharField(max_length=20, choices=SLOTS)
    class Meta:
        unique_together = (("day_plan","slot"),)

    def __str__(self):
        return f"{self.get_slot_display()} · {self.day_plan.date}"

class MealItem(TimeStampedModel):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="items")
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    portions = models.FloatField(default=1.0)
    protein_g = models.FloatField(default=0)
    carbs_g   = models.FloatField(default=0)
    fat_g     = models.FloatField(default=0)
    kcal      = models.FloatField(default=0)

    def __str__(self):
        return f"{self.recipe.name} × {self.portions}"

class MealItemIngredient(TimeStampedModel):
    G="g"; ML="ml"; P="piece"
    UNIT_CHOICES=[(G,"g"),(ML,"ml"),(P,"pieza")]

    meal_item = models.ForeignKey(MealItem, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.FloatField(validators=[MinValueValidator(0.0)])
    unit = models.CharField(max_length=8, choices=UNIT_CHOICES, default=G)

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount}{self.unit})"