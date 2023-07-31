from django.db import models

from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True, default=None)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
