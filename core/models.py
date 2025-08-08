from django.conf import settings
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    grocery_weekday = models.PositiveSmallIntegerField(default=0)  # 0=Lunes
    default_currency = models.CharField(max_length=8, default="MXN")

class Store(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)