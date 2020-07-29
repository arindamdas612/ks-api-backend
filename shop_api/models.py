from django.db import models
from django.conf import settings
import boto3


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=50)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    qty = models.IntegerField(default=0)
    marked_price = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    spec_title = models.CharField(max_length=100)
    spec_value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product.title} [ {self.spec_title}: {self.spec_value}]"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='product-images')

    def __str__(self):
        return f'{self.product.title} Image'

    def delete(self, *args, **kwargs):
        image_key = self.product_image.name
        super(ProductImage, self).delete(*args, **kwargs)
        session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_S3_REGION_NAME)
        s3 = session.resource('s3')
        obj = s3.Object(settings.AWS_STORAGE_BUCKET_NAME, image_key)
        # obj.delete()

    def get_image_url(self):
        return self.product_image.url.split('?')[0]
