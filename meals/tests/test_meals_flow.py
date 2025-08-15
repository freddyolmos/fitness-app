from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from nutrition.models import (
        IngredientCategory, 
        Ingredient, 
        Recipe, 
        RecipeIngredient
    )
from meals.models import (
    Meal,
    MealItemIngredient,
    MealItem,
    DayPlan,
)
from datetime import date

User = get_user_model()

class MealsFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass1234")
        self.client = APIClient()
        res = self.client.post(reverse("token_obtain_pair"), {"username": "u1", "password": "pass1234"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        cat = IngredientCategory.objects.create(name="Proteína")
        self.chicken = Ingredient.objects.create(
            name="Pechuga de pollo", category=cat, protein_g=31, carbs_g=0, fat_g=3.6, kcal=165
        )
        self.rice = Ingredient.objects.create(
            name="Arroz cocido", category=cat, protein_g=2.7, carbs_g=28, fat_g=0.3, kcal=130
        )
        self.recipe = Recipe.objects.create(name="Pollo con arroz", default_portion_grams=300)
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.chicken, amount=150, unit="g")
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.rice, amount=200, unit="g")

    def test_01_create_dayplan_autocreates_5_meals(self):
        res = self.client.post("/api/day-plans/", {"date": str(date.today())}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        dp_id = res.data["id"]
        meals = Meal.objects.filter(day_plan_id=dp_id).count()
        self.assertEqual(meals, 5)

    def test_02_create_mealitem_clones_and_sums(self):
        dp_res = self.client.post("/api/day-plans/", {"date": "2025-01-01"}, format="json")
        self.assertEqual(dp_res.status_code, status.HTTP_201_CREATED)
        dp_id = dp_res.data["id"]
        comida = Meal.objects.get(day_plan_id=dp_id, slot="comida")

        res = self.client.post("/api/meal-items/", {
            "meal": comida.id,
            "recipe": self.recipe.id,
            "portions": 1.0
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        item_id = res.data["id"]

        cloned = MealItemIngredient.objects.filter(meal_item_id=item_id).order_by("id")
        self.assertEqual(cloned.count(), 2)
        item = MealItem.objects.get(pk=item_id)
        self.assertGreater(item.protein_g, 0)
        self.assertGreater(item.kcal, 0)

        dp = DayPlan.objects.get(pk=dp_id)
        self.assertAlmostEqual(dp.kcal_total, item.kcal, places=2)

    def test_03_edit_mealitemingredient_recalculates(self):
        dp_res = self.client.post("/api/day-plans/", {"date": "2025-01-02"}, format="json")
        dp_id = dp_res.data["id"]
        comida = Meal.objects.get(day_plan_id=dp_id, slot="comida")
        item_res = self.client.post("/api/meal-items/", {
            "meal": comida.id, "recipe": self.recipe.id, "portions": 1.0
        }, format="json")
        item_id = item_res.data["id"]
        item_before = MealItem.objects.get(pk=item_id)

        rice_mii = MealItemIngredient.objects.get(meal_item_id=item_id, ingredient=self.rice)
        patch_res = self.client.patch(f"/api/meal-item-ingredients/{rice_mii.id}/", {
            "amount": rice_mii.amount + 100
        }, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)

        item_after = MealItem.objects.get(pk=item_id)
        dp_after = DayPlan.objects.get(pk=dp_id)
        self.assertGreater(item_after.kcal, item_before.kcal)
        self.assertGreater(dp_after.kcal_total, item_before.kcal)

    def test_04_delete_mealitem_updates_day_totals(self):
        dp_res = self.client.post("/api/day-plans/", {"date": "2025-01-03"}, format="json")
        dp_id = dp_res.data["id"]
        comida = Meal.objects.get(day_plan_id=dp_id, slot="comida")

        item1 = self.client.post("/api/meal-items/", {"meal": comida.id, "recipe": self.recipe.id, "portions": 1.0}, format="json").data
        item2 = self.client.post("/api/meal-items/", {"meal": comida.id, "recipe": self.recipe.id, "portions": 1.0}, format="json").data
        dp_mid = DayPlan.objects.get(pk=dp_id)
        total_mid = dp_mid.kcal_total

        del_res = self.client.delete(f"/api/meal-items/{item2['id']}/")
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

        dp_after = DayPlan.objects.get(pk=dp_id)
        self.assertLess(dp_after.kcal_total, total_mid)

    def test_05_recipe_preview_action(self):
        res = self.client.post(f"/api/recipes/{self.recipe.id}/preview?portions=1.5", {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("protein_g", res.data)
        self.assertEqual(float(res.data["portions"]), 1.5)