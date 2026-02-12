@echo off
echo ========================================
echo Django Auto-Unblock Setup
echo ========================================
echo.
echo This script will help you test the auto-unblock feature.
echo.
echo Current directory: %CD%
echo.

echo Testing the auto-unblock command...
python manage.py auto_unblock_expired

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run this automatically every day:
echo 1. Open Task Scheduler
echo 2. Create a new Basic Task
echo 3. Set it to run daily at 2:00 AM
echo 4. Action: Start a program
echo    - Program: python
echo    - Arguments: manage.py auto_unblock_expired
echo    - Start in: %CD%
echo.
echo See BLACKLIST_AUTO_UNBLOCK_SETUP.md for detailed instructions.
echo.
pause
