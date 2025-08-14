from typing import Tuple
from nutrition.models import Ingredient, Recipe
from django.db import models, transaction
from meals.models import MealItem

def _to_grams(ingredient: Ingredient, amount: float, unit: str) -> float:
    if unit == "g":
        return amount
    if unit == "ml":
        if ingredient.density_g_ml:
            return amount * ingredient.density_g_ml
        return amount
    if unit == "pieza":
        if ingredient.grams_per_piece:
            return amount * ingredient.grams_per_piece
        return amount
    return amount

def macros_from_ingredients(meal_item) -> tuple[float,float,float,float]:
    total_p = total_c = total_f = total_k = 0.0
    for mii in meal_item.ingredients.select_related("ingredient"):
        ing = mii.ingredient
        grams = _to_grams(ing, mii.amount, mii.unit)
        factor = grams / 100.0
        total_p += ing.protein_g * factor
        total_c += ing.carbs_g   * factor
        total_f += ing.fat_g     * factor
        k = ing.kcal if ing.kcal else (ing.protein_g*4 + ing.carbs_g*4 + ing.fat_g*9)
        total_k += k * factor
    return (round(total_p,2), round(total_c,2), round(total_f,2), round(total_k,2))

def calc_recipe_macros(recipe: Recipe, portions: float = 1.0) -> Tuple[float, float, float, float]:
    """
    Devuelve (protein_g, carbs_g, fat_g, kcal) para 'portions' porciones de la receta.
    Asume que las macros de Ingredient son por 100 g.
    """
    total_p = total_c = total_f = total_k = 0.0
    for ri in recipe.ingredients.select_related("ingredient").all():
        ing = ri.ingredient
        grams = _to_grams(ing, ri.amount, ri.unit)
        factor = grams / 100.0
        total_p += ing.protein_g * factor
        total_c += ing.carbs_g   * factor
        total_f += ing.fat_g     * factor
        k = ing.kcal if ing.kcal else (ing.protein_g*4 + ing.carbs_g*4 + ing.fat_g*9)
        total_k += k * factor
    return (round(total_p * portions, 2),
            round(total_c * portions, 2),
            round(total_f * portions, 2),
            round(total_k * portions, 2))

@transaction.atomic
def recalc_meal_item_and_day(meal_item):
    p,c,f,k = macros_from_ingredients(meal_item)
    MealItem.objects.filter(pk=meal_item.pk).update(
        protein_g=p, carbs_g=c, fat_g=f, kcal=k
    )
    day = meal_item.meal.day_plan
    agg = MealItem.objects.filter(meal__day_plan=day).aggregate(
        p=models.Sum("protein_g"), c=models.Sum("carbs_g"),
        f=models.Sum("fat_g"), k=models.Sum("kcal")
    )
    day.protein_total_g = round(agg["p"] or 0, 2)
    day.carbs_total_g   = round(agg["c"] or 0, 2)
    day.fat_total_g     = round(agg["f"] or 0, 2)
    day.kcal_total      = round(agg["k"] or 0, 2)
    day.save(update_fields=["protein_total_g","carbs_total_g","fat_total_g","kcal_total","updated_at"])