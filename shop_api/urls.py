from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryAdminViewSet


router = DefaultRouter()
router.register('category', CategoryAdminViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
