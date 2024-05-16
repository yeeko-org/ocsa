from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'


class User(AbstractUser):
    phone = models.CharField(max_length=100, blank=True)
    role = models.ManyToManyField(Role, blank=True)
