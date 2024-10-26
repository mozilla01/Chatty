from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Message, Room, Tags, Domain
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

# Create your views here.


@login_required(login_url='login')
def index(request):
    user_tags = Tags.objects.filter(users=request.user)

    # Step 2: Get all rooms with matching tags but exclude rooms hosted by the user
    rooms_with_matching_tags = Room.objects.filter(
        tags__in=user_tags  # Match rooms with user's tags
    ).exclude(
        host=request.user  # Exclude rooms hosted by the user
    ).distinct()  # Avoid duplicate rooms if they have multiple matching tags

    # Step 3: Attach any query messages for each room
    for room in rooms_with_matching_tags:
        # Retrieve messages with `query=True` for each room
        room.queries = Message.objects.filter(room=room, query=True)
    
    # Step 4: Render the result to the template
    return render(request, "chat/index.html", {"rooms": rooms_with_matching_tags, "tags": user_tags})

@login_required(login_url='login')
def room(request, room_name):
    messages = Message.objects.filter(room__name=room_name.lower())
    tags = Tags.objects.filter(rooms__name=room_name.lower())
    queries = Message.objects.filter(room__name=room_name.lower(), query=True)
    
    convo_string = ''
    for message in messages:
        convo_string += message.author.username + ': ' + message.content + '\n'

    return render(request, "chat/room.html", {"room_name": room_name, "messages": messages, "tags": tags, "queries": queries, "convo_string": convo_string})

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = User.objects.create_user(username=username, password=password)
        user.save()
        return redirect('login')
    else:
        return render(request, "chat/register.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/chat')
        else:
            return redirect('/login')
    else:
        return render(request, 'chat/login.html')

def logout(request):
    logout(request)
    return render('/chat')

class RoomSerializer(serializers.Serializer):
    convo_string = serializers.CharField()
    class Meta:
        model = Room
        fields = '__all__'

class GetUserConversations(APIView):
    
    def get(self, request):
        # Get conversation strings for user's rooms
        user_rooms = Room.objects.filter(host=request.user)
        for room in user_rooms:
            messages = Message.objects.filter(room__name=room.name.lower())
            convo_string = 'Room: ' + room.name + '\n'
            for message in messages:
                convo_string += message.author.username + ': ' + message.content + '\n'
            room.convo_string = convo_string
        serializer = RoomSerializer(user_rooms, many=True)
            
        return Response(serializer.data)