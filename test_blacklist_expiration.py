"""
Test script for blacklist auto-expiration feature
Run with: python manage.py shell < test_blacklist_expiration.py
"""

from django.utils import timezone
from datetime import timedelta
from user_account.models import Patient, Practitioner
from practitionerdashboard.models import PatientBlacklist

print("\n" + "="*60)
print("BLACKLIST AUTO-EXPIRATION TEST")
print("="*60 + "\n")

# Get counts
total_blacklists = PatientBlacklist.objects.count()
active_blacklists = PatientBlacklist.objects.filter(is_active=True).count()
temporary_blacklists = PatientBlacklist.objects.filter(is_permanent=False).count()

print(f"📊 Current Statistics:")
print(f"   Total blacklist entries: {total_blacklists}")
print(f"   Active blacklists: {active_blacklists}")
print(f"   Temporary blacklists: {temporary_blacklists}")
print()

# Check for entries with expiration dates
today = timezone.now().date()
expired_count = PatientBlacklist.objects.filter(
    is_active=True,
    is_permanent=False,
    unblock_date__lte=today
).count()

upcoming_expiry = PatientBlacklist.objects.filter(
    is_active=True,
    is_permanent=False,
    unblock_date__gt=today,
    unblock_date__lte=today + timedelta(days=7)
).count()

print(f"⏰ Expiration Status:")
print(f"   Expired (ready to unblock): {expired_count}")
print(f"   Expiring in next 7 days: {upcoming_expiry}")
print()

# Show some sample entries
print("📋 Sample Blacklist Entries:")
sample_entries = PatientBlacklist.objects.filter(is_active=True)[:5]

if sample_entries:
    for entry in sample_entries:
        status = "EXPIRED" if entry.unblock_date and entry.unblock_date <= today else "ACTIVE"
        expiry_info = f"expires {entry.unblock_date}" if entry.unblock_date else "permanent"
        
        print(f"\n   Patient: {entry.patient.first_name} {entry.patient.last_name}")
        print(f"   Practitioner: Dr. {entry.practitioner.first_name} {entry.practitioner.last_name}")
        print(f"   Status: {status}")
        print(f"   Blacklisted: {entry.blacklisted_at.strftime('%Y-%m-%d')}")
        print(f"   Expiration: {expiry_info}")
        print(f"   Reason: {entry.get_reason_display()}")
else:
    print("   No active blacklist entries found")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\n💡 To manually unblock expired entries, run:")
print("   python manage.py auto_unblock_expired")
print()
