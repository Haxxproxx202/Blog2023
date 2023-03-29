from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUserModel(AbstractUser):
    class UserType(models.TextChoices):
        BASIC = 'BASIC', _('Basic')
        EXTRA = 'EXTRA', _('Extra')
        ADMIN = 'ADMIN', _('Admin')

    default_type = UserType.BASIC
    type = models.CharField(max_length=5, choices=UserType.choices, default=default_type)
    email = models.EmailField(max_length=30, blank=False, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]
