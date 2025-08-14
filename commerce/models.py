from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from core.models import TimeStampedModel, Store
from nutrition.models import Ingredient

class InventoryItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventory")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    available = models.BooleanField(default=False)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "ingredient"], name="uniq_inventory_user_ingredient"),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["ingredient"]),
            models.Index(fields=["available"]),
        ]
        ordering = ("-updated_at",)

    def __str__(self):
        return f"{self.ingredient.name} @ {self.user}"

class IngredientPrice(TimeStampedModel):
    KG="kg"; G="g"; L="L"; ML="ml"; PIECE="piece"
    UNIT_CHOICES=[(KG,"kg"),(G,"g"),(L,"L"),(ML,"ml"),(PIECE,"pieza")]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="prices")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="prices")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=KG)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=8, default="MXN")
    observed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["ingredient"]),
            models.Index(fields=["store"]),
            models.Index(fields=["observed_at"]),
        ]
        ordering = ("-observed_at",)

    def __str__(self):
        return f"{self.ingredient.name} - {self.store.name} ({self.unit} {self.currency})"