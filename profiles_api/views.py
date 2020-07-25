from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from profiles_api import serializers
from profiles_api import models
from profiles_api import permissions


class UserProfileViewSet(viewsets.ModelViewSet):
    """Handle creating and updating profiles"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile, IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email')


class UserLoginAPIView(ObtainAuthToken):
    """Handle creating user Authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
