from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializes a Category Object"""

    class Meta:
        model = Category
        fields = ('id', 'name', 'description')

    def create(self, validated_data):
        new_Category = Category.objects.create(name=validated_data['name'],
                                               description=validated_data['description'])
        return new_Category
