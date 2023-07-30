from django.db import models

from users.models import User


class Room(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    is_closed = models.BooleanField(default=True, blank=False, null=False)


class Message(models.Model):
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    text = models.TextField()
    time = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(null=False, blank=False)
