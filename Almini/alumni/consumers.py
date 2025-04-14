import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, MentorshipRequest
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.request_id = self.scope['url_route']['kwargs']['request_id']
        self.room_group_name = f'chat_{self.request_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Save message to database
        await self.save_message(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope['user'].get_full_name(),
                'timestamp': timezone.now().strftime("%b %d, %Y %I:%M %p")
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'is_own': self.scope['user'].get_full_name() == event['sender']
        }))

    @database_sync_to_async
    def save_message(self, message):
        request = MentorshipRequest.objects.get(id=self.request_id)
        Message.objects.create(
            mentorship_request=request,
            sender=self.scope['user'].alumniprofile,
            message=message
        )