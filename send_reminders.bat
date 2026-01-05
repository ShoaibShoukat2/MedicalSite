@echo off
REM Medical Platform - Appointment Reminder Batch Script
REM This script sends appointment reminders to patients

echo Medical Platform - Sending Appointment Reminders
echo ================================================

REM Change to the project directory (update this path to your project location)
cd /d "D:\CLientProjects\MedicalProject\MedicalSite"

echo.
echo Sending 24-hour reminders...
python manage.py send_appointment_reminders --hours=24

echo.
echo Sending 2-hour reminders...
python manage.py send_appointment_reminders --hours=2

echo.
echo Reminder sending completed!
echo Check the output above for any errors.

pause