from django.urls import path
from django.shortcuts import render
from . import views
urlpatterns = [
    path('', views.ai_chat_view, name='ai_chat'),
]
