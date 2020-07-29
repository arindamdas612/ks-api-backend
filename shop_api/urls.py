from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryAdminViewSet, ProductCreateAdminApiView, ProductUpdateAdminApiView


router = DefaultRouter()
router.register('category', CategoryAdminViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('product/', ProductCreateAdminApiView.as_view()),
    path('product/update/', ProductUpdateAdminApiView.as_view()),
]
