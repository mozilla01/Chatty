from django.contrib import admin
from .models import Room, Message, Tags, Domain

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Tags)
admin.site.register(Domain)
