from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'ai_chatbot'

urlpatterns = [
    path('', views.ai_chat_view, name='ai_chat'),
    path('ask-avatar/', views.ask_avatar, name='ask_avatar'),
]
