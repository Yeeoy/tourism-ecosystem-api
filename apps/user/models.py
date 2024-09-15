from django.contrib.auth.models import (
    AbstractBaseUser,  # AbstractBaseUser是Django提供的一个基类，用于自定义用户模型
    BaseUserManager,  # BaseUserManager是Dango自定义用户模型的管理类，可以控制用户创建流程
    PermissionsMixin  # PermissionsMixin是Django提供的一个基类，用于添加用户权限相关的功能
)
from django.db import models


# Create your models here.
# 自定义用户管理类
class UserManager(BaseUserManager):
    # 创建用户
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # 创建超级用户
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


# 自定义用户模型
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
