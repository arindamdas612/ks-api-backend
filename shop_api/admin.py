from django.contrib import admin
from .models import Category, Product, ProductSpecification, ProductImage

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductSpecification)
admin.site.register(ProductImage)
