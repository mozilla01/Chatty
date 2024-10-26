from django.urls import path
from . import views

urlpatterns = [
    path("", views.ask_domain, name="askDomain"),
    path("tags/", views.ask_tags, name="askTags"),
    path("domain/", views.get_domain, name="getDomain"),
    path('submit-quiz/', views.submit_quiz, name='submitQuiz'),
    path('change-badge-url/', views.change_badge, name='changeBadge'),
    path('verify-expert/', views.verify_expert, name='verifyExpert'),

]
