from django.core.management.base import BaseCommand
from patientdashboard.models import Appointment
from chat.models import ChatRoom

class Command(BaseCommand):
    help = 'Test appointment acceptance flow'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Testing appointment acceptance flow...")
        
        # Get all accepted appointments
        accepted_appointments = Appointment.objects.filter(status='Accepted')
        
        self.stdout.write(f"📊 Found {accepted_appointments.count()} accepted appointments")
        
        for appointment in accepted_appointments:
            self.stdout.write(f"\n📋 Appointment {appointment.id}:")
            self.stdout.write(f"   Patient: {appointment.patient.first_name} {appointment.patient.last_name}")
            self.stdout.write(f"   Practitioner: Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name}")
            self.stdout.write(f"   Status: {appointment.status}")
            self.stdout.write(f"   Video Link: {appointment.video_call_link or 'None'}")
            self.stdout.write(f"   Meeting ID: {appointment.meeting_id or 'None'}")
            
            # Check if chat room exists
            try:
                chat_room = ChatRoom.objects.get(
                    patient=appointment.patient,
                    practitioner=appointment.practitioner
                )
                self.stdout.write(f"   Chat Room: ✅ Exists (ID: {chat_room.id})")
            except ChatRoom.DoesNotExist:
                self.stdout.write(f"   Chat Room: ❌ Missing")
                
                # Create missing chat room
                chat_room = ChatRoom.objects.create(
                    patient=appointment.patient,
                    practitioner=appointment.practitioner
                )
                self.stdout.write(f"   Chat Room: ✅ Created (ID: {chat_room.id})")
        
        self.stdout.write("\n✅ Test completed!")