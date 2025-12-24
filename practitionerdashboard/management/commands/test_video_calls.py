from django.core.management.base import BaseCommand
from patientdashboard.models import Appointment
from practitionerdashboard.views import generate_zoom_meeting_for_appointment, ZOOM_CONFIGURED

class Command(BaseCommand):
    help = 'Test video call system'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Testing video call system...")
        
        # Check Zoom configuration
        if ZOOM_CONFIGURED:
            self.stdout.write("✅ Zoom API is configured")
        else:
            self.stdout.write("⚠️ Zoom API not configured - using Jitsi fallback")
        
        # Get accepted appointments without video links
        appointments_without_video = Appointment.objects.filter(
            status='Accepted',
            video_call_link__isnull=True
        )
        
        self.stdout.write(f"📊 Found {appointments_without_video.count()} accepted appointments without video links")
        
        # Test meeting generation for first appointment
        if appointments_without_video.exists():
            appointment = appointments_without_video.first()
            self.stdout.write(f"\n🧪 Testing meeting generation for appointment {appointment.id}")
            
            result = generate_zoom_meeting_for_appointment(appointment)
            
            if result['success']:
                provider = result.get('provider', 'unknown')
                self.stdout.write(f"✅ {provider.title()} meeting created successfully!")
                self.stdout.write(f"   Meeting ID: {result['meeting_id']}")
                self.stdout.write(f"   Join URL: {result['join_url']}")
                self.stdout.write(f"   Provider: {provider}")
            else:
                self.stdout.write(f"❌ Meeting creation failed: {result['error']}")
        
        # Check all accepted appointments
        accepted_appointments = Appointment.objects.filter(status='Accepted')
        
        self.stdout.write(f"\n📋 Checking all {accepted_appointments.count()} accepted appointments:")
        
        for appointment in accepted_appointments:
            has_video = "✅" if appointment.video_call_link else "❌"
            provider = "Unknown"
            
            if appointment.video_call_link:
                if "zoom.us" in appointment.video_call_link:
                    provider = "Zoom"
                elif "meet.jit.si" in appointment.video_call_link:
                    provider = "Jitsi"
                else:
                    provider = "Other"
            
            self.stdout.write(f"   Appointment {appointment.id}: {has_video} Video Link ({provider})")
        
        self.stdout.write("\n✅ Test completed!")