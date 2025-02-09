# apps/accounts/api/v1/views.py
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from apps.accounts.api.v1.serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer