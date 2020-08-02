from django.contrib import admin
from .models import Order, OrderItem, OrderActivity

# Register your models here.


admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(OrderActivity)
