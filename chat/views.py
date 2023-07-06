from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Message


# Create your views here.


@login_required(login_url='login')
def index(request):
    return render(request, "chat/index.html")

@login_required(login_url='login')
def room(request, room_name):
    messages = Message.objects.filter(room__name=room_name.lower())
    return render(request, "chat/room.html", {"room_name": room_name, "messages": messages})

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
