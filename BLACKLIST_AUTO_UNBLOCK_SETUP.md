# Blacklist Auto-Unblock Feature

## Overview
Patients who are blacklisted (due to excessive cancellations or other reasons) will now be automatically unblocked after 30 days.

## How It Works

1. **When a patient is blacklisted:**
   - The system sets `is_permanent = False`
   - Sets `unblock_date` to 30 days from the blacklist date
   - The patient cannot book appointments during this period

2. **Automatic unblocking:**
   - A management command checks daily for expired blacklist entries
   - Patients whose `unblock_date` has passed are automatically unblocked
   - Practitioners receive a notification when a patient is auto-unblocked

## Setup Instructions

### Option 1: Manual Testing
Run the command manually to test:
```bash
python manage.py auto_unblock_expired
```

### Option 2: Windows Task Scheduler (Recommended for Windows)

1. Open Task Scheduler (search for "Task Scheduler" in Windows)

2. Click "Create Basic Task"

3. Name: "Django Auto-Unblock Blacklisted Patients"
   Description: "Automatically unblock patients after 30 days"

4. Trigger: Daily at 2:00 AM (or your preferred time)

5. Action: Start a program
   - Program/script: `python`
   - Add arguments: `manage.py auto_unblock_expired`
   - Start in: `C:\path\to\your\project` (replace with your actual project path)

6. Finish and test the task

### Option 3: Linux/Mac Cron Job

1. Open crontab:
```bash
crontab -e
```

2. Add this line (runs daily at 2:00 AM):
```bash
0 2 * * * cd /path/to/your/project && /path/to/python manage.py auto_unblock_expired >> /var/log/django_auto_unblock.log 2>&1
```

Replace:
- `/path/to/your/project` with your actual project directory
- `/path/to/python` with your Python executable path (use `which python` to find it)

### Option 4: Django-Cron or Celery (For Production)

For production environments, consider using:
- **django-cron**: Simple periodic task runner
- **Celery**: More robust task queue system

## Features Implemented

1. ✅ Automatic 30-day expiration for blacklisted patients
2. ✅ Management command to check and unblock expired entries
3. ✅ Practitioner notifications when patients are auto-unblocked
4. ✅ Auto-check on blacklist view page load
5. ✅ Model method `check_and_auto_unblock()` for manual checks

## Model Changes

The `PatientBlacklist` model now includes:
- `is_permanent`: Boolean (default: False for new blacklists)
- `unblock_date`: Date field (automatically set to +30 days)
- `is_active`: Boolean to track if blacklist is currently active

## Testing

To test the feature:

1. Blacklist a patient
2. Check the database - `unblock_date` should be 30 days in the future
3. Manually set `unblock_date` to today or yesterday
4. Run: `python manage.py auto_unblock_expired`
5. Verify the patient is unblocked (is_active = False)
6. Check that practitioner received a notification

## Notes

- Existing blacklist entries will need to be updated manually if you want them to expire
- Practitioners can still manually remove patients from the blacklist at any time
- The 30-day period can be adjusted in the code if needed (search for `timedelta(days=30)`)
