from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True, null=True)

class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    content = models.TextField(max_length=1000)
    query = models.BooleanField(default=False)

class Domain(models.Model):
    name = models.CharField(max_length=50)

class Tags(models.Model):
    name = models.CharField(max_length=50)
    rooms = models.ManyToManyField(Room)
    users = models.ManyToManyField(User)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True)