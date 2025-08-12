from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class IngredientCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)