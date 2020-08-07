from django.urls import path, include
from rest_framework.routers import DefaultRouter
from profiles_api import views


router = DefaultRouter()
router.register('profile', views.UserProfileViewSet)


urlpatterns = [
    path('login/', views.UserLoginAPIView.as_view()),
    path('', include(router.urls)),
    path('all-users/', views.UserManageApiView.as_view()),
    path('dashboard/', views.AdminDashboardDatapoints.as_view()),
]
