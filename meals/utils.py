from typing import Tuple
from nutrition.models import Ingredient, Recipe

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
