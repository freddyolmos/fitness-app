from rest_framework import viewsets, permissions
from .models import UserProfile, Store
from .serializers import UserProfileSerializer, StoreSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    permissions_classes = [permissions.IsAuthenticated]

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all().order_by("name")
    serializer_class = StoreSerializer
    permissions_classes = [permissions.IsAuthenticated]