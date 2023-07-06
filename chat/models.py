from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    content = models.TextField(max_length=1000)
