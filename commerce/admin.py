from django.contrib import admin
from .models import InventoryItem, IngredientPrice

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("user", "ingredient", "available", "last_checked_at", "updated_at")
    list_filter = ("available",)
    search_fields = ("user__username", "user__email", "ingredient__name")

@admin.register(IngredientPrice)
class IngredientPriceAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "store", "unit", "price_per_unit", "currency", "observed_at")
    list_filter = ("store", "unit", "currency")
    search_fields = ("ingredient__name", "store__name")
    date_hierarchy = "observed_at"