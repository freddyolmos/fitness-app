from rest_framework import serializers
from .models import InventoryItem, IngredientPrice
from nutrition.models import Ingredient

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = "__all__"

class IngredientPriceSerializer(serializers.ModelSerializer):
    price_per_100g = serializers.SerializerMethodField()

    class Meta:
        model = IngredientPrice
        fields = "__all__"

    def get_price_per_100g(self, obj):
        ing: Ingredient = obj.ingredient
        p = float(obj.price_per_unit)
        if obj.unit == obj.KG:
            return round(p / 10.0, 2)
        if obj.unit == obj.G:
            return round(p * 100.0, 2)
        if obj.unit in (obj.L, obj.ML):
            if not ing.density_g_ml:
                return None
            grams = 1000.0 if obj.unit == obj.L else 1.0
            grams *= ing.density_g_ml
            factor = (100.0 / grams)
            return round(p * factor, 2)
        if obj.unit == obj.PIECE:
            if not ing.grams_per_piece or ing.grams_per_piece <= 0:
                return None
            return round(p * (100.0 / ing.grams_per_piece), 2)
        return None
