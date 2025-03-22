from rest_framework import serializers
from .models import Message, ChatRoom

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'
