from django.core.management.base import BaseCommand
from django.utils import timezone
from practitionerdashboard.models import PatientBlacklist
from practitionerdashboard.notifications import create_practitioner_notification


class Command(BaseCommand):
    help = 'Automatically unblock patients whose blacklist period has expired'

    def handle(self, *args, **options):
        """
        Check all active blacklist entries and unblock those that have expired.
        This should be run daily via a cron job or task scheduler.
        """
        today = timezone.now().date()
        
        # Find all active, non-permanent blacklist entries that have expired
        expired_blacklists = PatientBlacklist.objects.filter(
            is_active=True,
            is_permanent=False,
            unblock_date__lte=today
        )
        
        unblocked_count = 0
        
        for blacklist_entry in expired_blacklists:
            patient = blacklist_entry.patient
            practitioner = blacklist_entry.practitioner
            
            # Unblock the patient
            blacklist_entry.is_active = False
            blacklist_entry.save()
            
            # Notify the practitioner
            create_practitioner_notification(
                practitioner=practitioner,
                title="Patient Automatically Unblocked",
                message=f"Patient {patient.first_name} {patient.last_name} has been automatically removed from your blacklist after 30 days.",
                notification_type='info',
                url='/practitioner-dashboard/blacklist/'
            )
            
            unblocked_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Unblocked: {patient.first_name} {patient.last_name} '
                    f'(Practitioner: Dr. {practitioner.first_name} {practitioner.last_name})'
                )
            )
        
        if unblocked_count == 0:
            self.stdout.write(self.style.WARNING('No expired blacklist entries found.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully unblocked {unblocked_count} patient(s).'
                )
            )
