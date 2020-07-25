from rest_framework import serializers
from profiles_api import models


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes a User Profile Object"""

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'name', 'mobile', 'password', 'is_superuser')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            }
        }

    def create(self, validated_date):
        """Create and return a new user"""
        user = models.UserProfile.objects.create_user(
            email=validated_date['email'],
            name=validated_date['name'],
            mobile=validated_date['mobile'],
            password=validated_date['password']
        )
        return user
