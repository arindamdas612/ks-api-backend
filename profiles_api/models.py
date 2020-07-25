from django.db import models

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager


class UserProfileManager(BaseUserManager):
    """Manger for User Profiles"""

    def create_user(self, email, name, mobile, password=None):
        """create a new user profile"""
        if not email:
            raise ValueError("Users must have an E-Mail Address")

        user = self.model(email=email, name=name, mobile=mobile)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, mobile, password):
        """Create and save new Super user with given detils"""
        user = self.create_user(email, name, mobile, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Databse Model for the user in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile']

    def get_full_name(self):
        """Retrieve Full name of user"""
        return self.name

    def get_short_name(self):
        """Retrieve Short name of user"""
        return str(self.name).split(' ')[0]

    def __str__(self):
        """Return string representaion of user"""
        return self.email
