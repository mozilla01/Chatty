from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.index, name="index"),
    path("chat/<str:room_name>/", views.room, name="room"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path('get-user-convo/', views.GetUserConversations.as_view(), name='get-user-convo'),
]
