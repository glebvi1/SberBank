from django.db import models

from users.models import User


class Ban(models.Model):
    banned_user = models.OneToOneField(to=User, blank=False, null=False, on_delete=models.CASCADE)
    reason = models.TextField(max_length=1000, blank=False, null=False)
