from django.db import models
from django.conf import settings
from user_account.models import Patient,Practitioner
class ChatRoom(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chatrooms')
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name='chatrooms')
    # other fields for chat room
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ai_enabled = models.BooleanField(default=False)
    ai_config = models.JSONField(default=dict, blank=True)  # Store AI preferences


    
    class Meta:
        unique_together = ['patient', 'practitioner']

    def __str__(self):
        return f"Chat between {self.patient} and {self.practitioner}"

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages',null=True)
    sender_type = models.CharField(max_length=20,null=True, choices=[
        ('patient', 'Patient'),
        ('practitioner', 'Practitioner')
    ])
    sender_id = models.IntegerField(null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender_type} at {self.timestamp}"
