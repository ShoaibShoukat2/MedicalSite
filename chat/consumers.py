import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.services import HealthcareAIAgent
from .models import ChatRoom, Message

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Handles new WebSocket connections"""
        try:
            # Extract room ID from URL
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            
            logger.info(f"Attempting connection - Room ID: {self.room_id}")
            
            # Retrieve session data (fix potential missing session)
            session = self.scope.get('session', {})
            self.user_id = session.get('patient_id') or session.get('practitioner_id')
            self.user_type = 'patient' if session.get('patient_id') else 'practitioner'
            
            if not self.user_id:
                logger.error("User ID not found in session. Closing connection.")
                await self.close()
                return

            logger.info(f"User Type: {self.user_type}, User ID: {self.user_id}")

            # Verify room access
            if not await self.verify_room_access():
                logger.error(f"Access denied to room {self.room_id} for user {self.user_id}")
                await self.close()
                return

            # Add user to the chat group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"WebSocket connection established for room {self.room_id}")

        except Exception as e:
            logger.error(f"Error during WebSocket connection: {str(e)}")
            await self.close()

    @database_sync_to_async
    def verify_room_access(self):
        """Checks if the user has access to the chat room"""
        try:
            if self.user_type == 'patient':
                return ChatRoom.objects.filter(id=self.room_id, patient_id=self.user_id).exists()
            else:
                return ChatRoom.objects.filter(id=self.room_id, practitioner_id=self.user_id).exists()
        except Exception as e:
            logger.error(f"Database error while verifying room access: {str(e)}")
            return False

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        logger.info(f"Disconnecting - Room: {self.room_id}, Code: {close_code}")
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        
        if not message:
            return
            
        # Save user message
        saved_message = await self.save_message(message)
        
        # Check if AI should respond
        chat_room = await self.get_chat_room()
        if chat_room.ai_enabled and saved_message.sender_type == 'patient':
            # Get message history for context
            history = await self.get_message_history()
            
            # Get AI response
            ai_agent = HealthcareAIAgent()
            ai_response = await ai_agent.get_response(history, message)
            
            # Save and broadcast AI response
            ai_message = await self.save_message(ai_response, is_ai=True)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_response,
                    'sender_type': 'practitioner',
                    'sender_id': chat_room.practitioner.id,
                    'is_ai': True,
                    'timestamp': ai_message.timestamp.isoformat()
                }
            )
        
        # Broadcast original message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_type': self.user_type,
                'sender_id': self.user_id,
                'timestamp': saved_message.timestamp.isoformat()
            }
        )

    @database_sync_to_async
    def get_chat_room(self):
        return ChatRoom.objects.get(id=self.room_id)
        
    @database_sync_to_async
    def get_message_history(self):
        return list(Message.objects.filter(
            chat_room_id=self.room_id
        ).order_by('-timestamp')[:10][::-1])

    async def chat_message(self, event):
        """Handles broadcasting messages to WebSocket clients"""
        try:
            await self.send(text_data=json.dumps(event))
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

    @database_sync_to_async
    def save_message(self, message, is_ai=False):
        try:
            room = ChatRoom.objects.get(id=self.room_id)  # Ensure correct room reference
            sender_type = 'practitioner' if is_ai else self.user_type
            sender_id = room.practitioner.id if is_ai else self.user_id

            return Message.objects.create(
                chat_room=room,
                sender_type=sender_type,
                sender_id=sender_id,
                content=message
        )
        except ChatRoom.DoesNotExist:
            logger.error(f"ChatRoom with ID {self.room_id} does not exist.")
            return None
        except Exception as e:
            logger.error(f"Error saving message to database: {str(e)}")
            return None

