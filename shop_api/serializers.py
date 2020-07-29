from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializes a Category Object"""

    class Meta:
        model = Category
        fields = ('id', 'name', 'description')

    def create(self, validated_data):
        new_Category = Category.objects.create(name=validated_data['name'],
                                               description=validated_data['description'])
        return new_Category


class ProductImageSerializer(serializers.Serializer):
    photo = serializers.ListField(child=serializers.ImageField(required=True))

    def create(self, validated_data):

        prod_id = self.context['prod_id']
        for attr, value in validated_data.items():
            if attr == 'photo':
                for x in value:
                    c = ProductImage.objects.create(product=Product.objects.get(
                        pk=prod_id), product_image=x)
                    c.save()
        return validated_data

