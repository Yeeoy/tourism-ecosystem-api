from django.contrib.auth.models import (
    AbstractBaseUser,  # AbstractBaseUser is a base class provided by Django for custom user models
    BaseUserManager,  # BaseUserManager is a manager class for custom user models, controlling the user creation process
    PermissionsMixin  # PermissionsMixin is a base class provided by Django for adding user permissions functionality
)
from django.db import models

from tourism_ecosystem import settings


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


class EventLog(models.Model):
    """
    Model for storing request and response event log data
    """
    case_id = models.CharField(max_length=255)  # Session ID or business process ID
    activity = models.CharField(max_length=255)  # Activity name or operation description
    start_time = models.DateTimeField()  # Request start time
    end_time = models.DateTimeField(null=True, blank=True)  # Request end time
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL)  # Foreign key referencing custom user model
    user_name = models.CharField(max_length=255, null=True, blank=True)  # User's name or username
    status_code = models.IntegerField(null=True, blank=True)  # Status code (for response)

    def __str__(self):
        return f"Case ID: {self.case_id}, Activity: {self.activity}, Start Time: {self.start_time}, End Time: {self.end_time}, User: {self.user}, User Name: {self.user_name}, Status: {self.status_code}"
