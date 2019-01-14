from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    skype = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=300, blank=True)
    facebook = models.TextField(max_length=100,null=True, blank=True)
    avatar = models.CharField(max_length=200, null=True, blank=True)
    site = models.CharField(max_length=100, null=True, blank=True)
    linkedin = models.CharField(max_length=100,null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
