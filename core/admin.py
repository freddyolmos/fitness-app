from django.contrib import admin
from .models import UserProfile, Store

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    list_filter = ("default_currency", "grocery_weekday")
    search_fields = ("user__username", "user__email")

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)