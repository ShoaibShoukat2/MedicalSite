# consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message  # Add this import at the top

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        session = self.scope.get('session', {})
        self.user_id = session.get('patient_id') or session.get('practitioner_id')
        self.user_type = 'patient' if session.get('patient_id') else 'practitioner'
        
        if not self.user_id or not await self.verify_room_access():
            await self.close()
            return
            
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def verify_room_access(self):
        try:
            if self.user_type == 'patient':
                return ChatRoom.objects.filter(
                    id=self.room_id,
                    patient_id=self.user_id
                ).exists()
            else:
                return ChatRoom.objects.filter(
                    id=self.room_id,
                    practitioner_id=self.user_id
                ).exists()
        except Exception as e:
            logger.error(f"Error verifying room access: {str(e)}")
            return False

    @database_sync_to_async
    def save_message(self, message_text):
        chat_room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(
            chat_room=chat_room,
            sender_type=self.user_type,
            sender_id=self.user_id,
            content=message_text
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_text = data.get('message', '').strip()
            
            if not message_text:
                return
            
            saved_message = await self.save_message(message_text)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'sender_type': self.user_type,
                    'sender_id': self.user_id,
                    'timestamp': saved_message.timestamp.isoformat(),
                }
            )
                
        except Exception as e:
            logger.error(f"Error in receive method: {str(e)}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps(event))
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {str(e)}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)



