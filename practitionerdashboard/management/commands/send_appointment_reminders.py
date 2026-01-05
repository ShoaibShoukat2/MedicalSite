"""
Management command to send appointment reminders
Run this command via cron job or task scheduler
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from user_account.models import Appointment
from practitionerdashboard.notifications import notify_appointment_reminder

class Command(BaseCommand):
    help = 'Send appointment reminders to patients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours before appointment to send reminder (default: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )

    def handle(self, *args, **options):
        hours_before = options['hours']
        dry_run = options['dry_run']
        
        # Calculate the target time
        target_time = timezone.now() + timedelta(hours=hours_before)
        
        # Find appointments that need reminders
        appointments = Appointment.objects.filter(
            slot__start_time__range=[
                target_time - timedelta(minutes=30),
                target_time + timedelta(minutes=30)
            ],
            status='Accepted'
        ).select_related('patient', 'practitioner', 'slot')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would send {appointments.count()} reminders for appointments in {hours_before} hours')
            )
            for appointment in appointments:
                self.stdout.write(
                    f'  - {appointment.patient.first_name} {appointment.patient.last_name} '
                    f'with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name} '
                    f'at {appointment.slot.start_time}'
                )
            return
        
        sent_count = 0
        error_count = 0
        
        for appointment in appointments:
            try:
                notify_appointment_reminder(appointment, hours_before=hours_before)
                sent_count += 1
                self.stdout.write(
                    f'Sent reminder to {appointment.patient.first_name} {appointment.patient.last_name} '
                    f'for appointment with Dr. {appointment.practitioner.first_name} {appointment.practitioner.last_name}'
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send reminder for appointment {appointment.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Reminder sending completed: {sent_count} sent, {error_count} errors'
            )
        )