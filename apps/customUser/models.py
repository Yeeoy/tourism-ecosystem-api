from django.contrib.auth.models import (
    AbstractBaseUser,  # AbstractBaseUser is a base class provided by Django for custom user models
    BaseUserManager,  # BaseUserManager is a manager class for custom user models, controlling the user creation process
    PermissionsMixin  # PermissionsMixin is a base class provided by Django for adding user permissions functionality
)
from django.db import models


# Create your models here.
# Custom user manager class
class UserManager(BaseUserManager):
    # Create a user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # Create a superuser
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


# Custom user model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'