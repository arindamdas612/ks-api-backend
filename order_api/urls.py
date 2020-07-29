from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdersAdminApiView


# router = DefaultRouter()
# router.register('category', CategoryAdminViewSet)


urlpatterns = [
    path('order/', OrdersAdminApiView.as_view()),
]
