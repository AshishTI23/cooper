from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from users.manager import UserManager


# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        ("first name"), max_length=50, blank=True, db_index=True
    )
    middle_name = models.CharField(
        ("middle name"), max_length=50, blank=True, db_index=True
    )
    last_name = models.CharField(
        ("last name"), max_length=50, blank=True, db_index=True
    )
    email = models.EmailField(("email"), unique=True)
    phone = models.CharField(
        ("phone"), max_length=12, blank=True, db_index=True, unique=True
    )
    country = models.CharField(max_length=2, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(("created at"), auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(
        ("modified at"), auto_now=True, auto_now_add=False
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    def __str__(self):
        return self.email
