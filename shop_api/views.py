from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication

from .models import Category, Product
from .serializers import CategorySerializer


class CategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    authentication_classes = (TokenAuthentication,)
    serializer_class = CategorySerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
