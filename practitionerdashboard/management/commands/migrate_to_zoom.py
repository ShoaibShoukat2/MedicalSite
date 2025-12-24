"""
Django management command to migrate existing Jitsi appointments to Zoom
Usage: python manage.py migrate_to_zoom
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from patientdashboard.models import Appointment
from practitionerdashboard.views import generate_zoom_meeting_for_appointment


class Command(BaseCommand):
    help = 'Migrate existing Jitsi Meet appointments to Zoom meetings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )
        parser.add_argument(
            '--practitioner-id',
            type=int,
            help='Migrate appointments for specific practitioner only',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 Starting Jitsi to Zoom migration...\n')
        )

        # Build query
        query = Appointment.objects.filter(
            status='Accepted',
            video_call_link__icontains='meet.jit.si'
        )

        if options['practitioner_id']:
            query = query.filter(practitioner_id=options['practitioner_id'])
            self.stdout.write(f"📋 Filtering for practitioner ID: {options['practitioner_id']}")

        appointments_to_migrate = query.all()
        total_count = appointments_to_migrate.count()

        if total_count == 0:
            self.stdout.write(
                self.style.WARNING('✅ No Jitsi appointments found to migrate!')
            )
            return

        self.stdout.write(f"📊 Found {total_count} appointments to migrate")

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be made\n')
            )
            
            for appointment in appointments_to_migrate:
                self.stdout.write(
                    f"Would migrate: Appointment {appointment.id} - "
                    f"{appointment.patient.first_name} {appointment.patient.last_name} - "
                    f"Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name}"
                )
            return

        # Perform actual migration
        updated_count = 0
        failed_count = 0

        for appointment in appointments_to_migrate:
            try:
                self.stdout.write(
                    f"🔄 Migrating appointment {appointment.id}...", 
                    ending=''
                )

                # Generate Zoom meeting
                zoom_result = generate_zoom_meeting_for_appointment(appointment)

                if zoom_result['success']:
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(' ✅ Success')
                    )
                    
                    # Log details
                    self.stdout.write(
                        f"   Patient: {appointment.patient.first_name} {appointment.patient.last_name}"
                    )
                    self.stdout.write(
                        f"   Doctor: Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name}"
                    )
                    self.stdout.write(
                        f"   Meeting ID: {appointment.meeting_id}"
                    )
                    self.stdout.write(
                        f"   Join URL: {appointment.video_call_link}\n"
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f' ❌ Failed: {zoom_result["error"]}')
                    )

            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f' ❌ Error: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'📊 MIGRATION SUMMARY')
        )
        self.stdout.write(f'Total appointments: {total_count}')
        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated: {updated_count}')
        )
        
        if failed_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Failed migrations: {failed_count}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No failures! 🎉')
            )

        self.stdout.write('='*50)

        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Migration completed! {updated_count} appointments now use Zoom.'
                )
            )
            self.stdout.write(
                'ℹ️  Patients will be notified about the new meeting links.'
            )
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️  No appointments were migrated.')
            )