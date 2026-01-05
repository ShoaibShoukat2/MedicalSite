# 🏥 Medical Platform - Comprehensive Notification System

## Overview
This notification system provides comprehensive email and in-app notifications for both patients and practitioners throughout the appointment lifecycle.

## 🔔 Features

### For Patients:
- **Appointment Booking Confirmation** - Immediate notification when appointment is booked
- **Appointment Acceptance** - Notification when practitioner accepts the appointment
- **Appointment Cancellation** - Notification when appointment is cancelled (by practitioner or system)
- **Appointment Modification** - Notification when appointment time is changed
- **Appointment Reminders** - 24-hour and 2-hour reminders before appointments
- **New Availability Alerts** - Notification when preferred practitioners add new slots

### For Practitioners:
- **New Appointment Requests** - Immediate notification of new booking requests
- **Patient Cancellations** - Notification when patients cancel appointments
- **System Notifications** - Various system-related notifications

### Notification Channels:
- **Email Notifications** - Professional HTML email templates
- **In-App Notifications** - Real-time notifications in dashboard
- **SMS Support** - Framework ready for SMS integration

## 📧 Email Configuration

The system uses Gmail SMTP with the following configuration:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'shoaibahmadbhatti6252@gmail.com'
EMAIL_HOST_PASSWORD = 'qlye fqjt pkbv xbzl'  # App Password
DEFAULT_FROM_EMAIL = 'shoaibahmadbhatti6252@gmail.com'
```

## 🚀 Setup Instructions

### 1. Database Migration
Run the following commands to set up notification models:

```bash
python manage.py makemigrations patientdashboard
python manage.py makemigrations practitionerdashboard
python manage.py migrate
```

### 2. Test the System
Run the test script to verify everything is working:

```bash
python test_notifications.py
```

### 3. Setup Automated Reminders

#### For Linux/Mac (Cron Jobs):
Add these lines to your crontab (`crontab -e`):

```bash
# Send 24-hour appointment reminders daily at 9 AM
0 9 * * * cd /path/to/your/project && python manage.py send_appointment_reminders --hours=24

# Send 2-hour appointment reminders every hour
0 * * * * cd /path/to/your/project && python manage.py send_appointment_reminders --hours=2
```

#### For Windows (Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (Daily for 24-hour, Hourly for 2-hour reminders)
4. Set action to run: `python manage.py send_appointment_reminders --hours=24`
5. Or use the provided `send_reminders.bat` file

## 📁 File Structure

```
├── practitionerdashboard/
│   ├── notifications.py              # Main notification functions
│   ├── models.py                     # PractitionerNotification model
│   ├── views.py                      # Notification API endpoints
│   ├── management/
│   │   └── commands/
│   │       └── send_appointment_reminders.py  # Management command
│   └── urls.py                       # Notification URLs
├── patientdashboard/
│   ├── models.py                     # Patient Notification model
│   └── views.py                      # Patient notification views
├── templates/
│   └── emails/                       # Email templates
│       ├── appointment_booked_patient.html
│       ├── appointment_confirmed.html
│       ├── appointment_cancelled.html
│       ├── appointment_modified.html
│       ├── appointment_request_practitioner.html
│       ├── appointment_reminder.html
│       └── new_availability.html
├── test_notifications.py            # Test script
├── setup_reminders.py              # Setup script
└── send_reminders.bat              # Windows batch file
```

## 🔧 API Endpoints

### Practitioner Endpoints:
- `GET /practitioner-dashboard/api/notifications/` - Get notifications
- `POST /practitioner-dashboard/api/notifications/mark-read/` - Mark notification as read
- `POST /practitioner-dashboard/api/notifications/mark-all-read/` - Mark all as read
- `POST /practitioner-dashboard/api/appointments/{id}/{action}/` - Accept/decline appointments
- `POST /practitioner-dashboard/api/notify-availability/` - Notify about new availability

### Patient Endpoints:
- `POST /patient-dashboard/mark-notifications-read/` - Mark all notifications as read
- `POST /patient-dashboard/mark-notification-read/` - Mark specific notification as read
- `GET /patient-dashboard/notifications/` - View all notifications

## 📨 Email Templates

All email templates are professionally designed with:
- Responsive design for mobile and desktop
- Medical theme with appropriate colors
- Clear call-to-action buttons
- Professional branding
- Comprehensive appointment details

## 🔄 Notification Triggers

### Automatic Triggers:
1. **Appointment Booking** - When patient books an appointment
2. **Appointment Acceptance** - When practitioner accepts appointment
3. **Appointment Cancellation** - When appointment is cancelled by either party
4. **New Availability** - When practitioner adds new slots
5. **Scheduled Reminders** - 24 hours and 2 hours before appointments

### Manual Triggers:
- Practitioners can manually notify patients about new availability
- System administrators can send bulk notifications

## 🧪 Testing

### Test Individual Functions:
```bash
python test_notifications.py
```

### Test Reminder Commands:
```bash
# Dry run (shows what would be sent without sending)
python manage.py send_appointment_reminders --dry-run --hours=24

# Send actual reminders
python manage.py send_appointment_reminders --hours=24
python manage.py send_appointment_reminders --hours=2
```

## 📊 Monitoring

### Check Notification Status:
- Patient notifications: Django Admin → Patient Dashboard → Notifications
- Practitioner notifications: Django Admin → Practitioner Dashboard → Practitioner Notifications
- Email logs: Check server email logs for delivery status

### Common Issues:
1. **Email not sending**: Check Gmail app password and SMTP settings
2. **Notifications not appearing**: Check database migrations
3. **Reminders not working**: Verify cron jobs or scheduled tasks

## 🔐 Security Features

- CSRF protection on all endpoints
- User authentication required for all notification actions
- Email templates sanitize user input
- Rate limiting can be added for bulk notifications

## 🌟 Advanced Features

### Customization Options:
- Email template customization
- Notification timing customization
- Multi-language support ready
- SMS integration framework

### Future Enhancements:
- Push notifications for mobile apps
- WhatsApp integration
- Advanced scheduling options
- Notification preferences per user

## 📞 Support

For issues or questions:
1. Check the test script output: `python test_notifications.py`
2. Review Django logs for errors
3. Verify email configuration
4. Check database for notification records

## 🎉 Success Indicators

When working correctly, you should see:
- ✅ Emails being sent to patients and practitioners
- ✅ In-app notifications appearing in dashboards
- ✅ Notification counts updating in real-time
- ✅ Scheduled reminders being sent automatically

The notification system is now fully integrated and ready to enhance your medical platform's communication capabilities!