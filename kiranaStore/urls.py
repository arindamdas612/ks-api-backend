
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/1/', include('profiles_api.urls')),
    path('api/2/', include('shop_api.urls')),
]
