from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    marked_price = models.FloatField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
