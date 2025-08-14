from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from core.models import MinValueValidator

class IngredientCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self): 
        return self.name

class Ingredient(TimeStampedModel):
    MASS = "g"; VOLUME = "ml"; PIECE = "piece"
    UNIT_CHOICES = [(MASS,"g"), (VOLUME,"ml"), (PIECE,"pieza")]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(IngredientCategory, on_delete=models.SET_NULL, null=True)
    protein_g = models.FloatField(default=0, validators=[MinValueValidator(0)])
    carbs_g   = models.FloatField(default=0, validators=[MinValueValidator(0)])
    fat_g     = models.FloatField(default=0, validators=[MinValueValidator(0)])
    kcal      = models.FloatField(default=0, validators=[MinValueValidator(0)],blank=True)
    grams_per_piece = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    density_g_ml    = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    barcode = models.CharField(max_length=64, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = (("name","owner"),)

    def __str__(self): 
        return self.name

class IngredientAlias(TimeStampedModel):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=150)

    class Meta:
        unique_together = (("ingredient","alias"),)

class IngredientSource(TimeStampedModel):
    FDC = "FDC"; OFF = "OFF"; MANUAL = "MANUAL"
    SOURCE_CHOICES = [(FDC,"FDC"), (OFF,"OFF"), (MANUAL,"Manual")]
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="sources")
    source = models.CharField(max_length=12, choices=SOURCE_CHOICES)
    external_id = models.CharField(max_length=100, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (("ingredient","source","external_id"),)

class Recipe(TimeStampedModel):
    FOOD="food"; BEVERAGE="beverage"
    KIND_CHOICES=[(FOOD,"Comida"),(BEVERAGE,"Bebida")]

    name = models.CharField(max_length=150)
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=FOOD)
    default_portion_grams = models.FloatField(default=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = (("name","owner"),) 

    def __str__(self): 
        return self.name

class RecipeIngredient(TimeStampedModel):
    G="g"; ML="ml"; P="piece"
    UNIT_CHOICES=[(G,"g"),(ML,"ml"),(P,"pieza")]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.FloatField()
    unit = models.CharField(max_length=8, choices=UNIT_CHOICES, default=G)

    class Meta:
        unique_together = (("recipe","ingredient"),)
        indexes = [models.Index(fields=["recipe"])]