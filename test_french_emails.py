"""
Test script to verify French email notifications are working
Run this to test: python test_french_emails.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.conf import settings
from django.template.loader import get_template
from practitionerdashboard.notifications import send_email_notification, translate_subject_to_french

def test_french_configuration():
    """Test 1: Verify Django is configured for French"""
    print("\n" + "="*60)
    print("TEST 1: Django Language Configuration")
    print("="*60)
    
    print(f"✓ LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
    
    if settings.LANGUAGE_CODE == 'fr':
        print("✅ PASS: Django is configured for French")
        return True
    else:
        print("❌ FAIL: Django is NOT configured for French")
        return False

def test_french_templates_exist():
    """Test 2: Verify all French email templates exist"""
    print("\n" + "="*60)
    print("TEST 2: French Email Templates")
    print("="*60)
    
    templates = [
        'emails/fr/appointment_booked_patient.html',
        'emails/fr/appointment_confirmed.html',
        'emails/fr/appointment_cancelled_patient.html',
        'emails/fr/appointment_cancelled_practitioner.html',
        'emails/fr/appointment_reminder.html',
        'emails/fr/appointment_modified.html',
        'emails/fr/appointment_request_practitioner.html',
        'emails/fr/new_availability.html',
    ]
    
    all_exist = True
    for template in templates:
        try:
            get_template(template)
            print(f"✓ Found: {template}")
        except Exception as e:
            print(f"✗ Missing: {template}")
            all_exist = False
    
    if all_exist:
        print("\n✅ PASS: All French templates exist")
        return True
    else:
        print("\n❌ FAIL: Some French templates are missing")
        return False

def test_subject_translation():
    """Test 3: Verify subject translation function"""
    print("\n" + "="*60)
    print("TEST 3: Subject Translation")
    print("="*60)
    
    test_cases = {
        'Appointment Booked': 'Rendez-vous Réservé',
        'Appointment Confirmed': 'Rendez-vous Confirmé',
        'Appointment Cancelled': 'Rendez-vous Annulé',
        'Patient Cancelled Appointment': 'Patient a Annulé le Rendez-vous',
        'Appointment Reminder': 'Rappel de Rendez-vous',
    }
    
    all_pass = True
    for english, expected_french in test_cases.items():
        result = translate_subject_to_french(english)
        if result == expected_french:
            print(f"✓ '{english}' → '{result}'")
        else:
            print(f"✗ '{english}' → '{result}' (expected: '{expected_french}')")
            all_pass = False
    
    if all_pass:
        print("\n✅ PASS: All subjects translate correctly")
        return True
    else:
        print("\n❌ FAIL: Some translations are incorrect")
        return False

def test_notification_function_signature():
    """Test 4: Verify send_email_notification has French as default"""
    print("\n" + "="*60)
    print("TEST 4: Notification Function Default Language")
    print("="*60)
    
    import inspect
    sig = inspect.signature(send_email_notification)
    
    print(f"Function signature: {sig}")
    
    # Check if language parameter has 'fr' as default
    if 'language' in sig.parameters:
        default = sig.parameters['language'].default
        print(f"✓ Language parameter default: '{default}'")
        
        if default == 'fr':
            print("\n✅ PASS: Default language is French")
            return True
        else:
            print(f"\n❌ FAIL: Default language is '{default}', not 'fr'")
            return False
    else:
        print("\n❌ FAIL: No language parameter found")
        return False

def test_template_content():
    """Test 5: Verify French templates contain French text"""
    print("\n" + "="*60)
    print("TEST 5: French Template Content Verification")
    print("="*60)
    
    # Test one template to verify it's actually in French
    try:
        template = get_template('emails/fr/appointment_confirmed.html')
        content = template.template.source
        
        # Check for French keywords
        french_keywords = [
            'Rendez-vous',
            'Confirmé',
            'Médecin',
            'Bonjour',
            'Cher',
        ]
        
        found_keywords = []
        for keyword in french_keywords:
            if keyword in content:
                found_keywords.append(keyword)
                print(f"✓ Found French keyword: '{keyword}'")
        
        if len(found_keywords) >= 3:
            print(f"\n✅ PASS: Template contains French content ({len(found_keywords)}/{len(french_keywords)} keywords found)")
            return True
        else:
            print(f"\n❌ FAIL: Template may not be in French ({len(found_keywords)}/{len(french_keywords)} keywords found)")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL: Error reading template: {str(e)}")
        return False

def run_all_tests():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("🇫🇷 FRENCH EMAIL NOTIFICATION VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run all tests
    results.append(("Django Configuration", test_french_configuration()))
    results.append(("French Templates", test_french_templates_exist()))
    results.append(("Subject Translation", test_subject_translation()))
    results.append(("Function Default", test_notification_function_signature()))
    results.append(("Template Content", test_template_content()))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 SUCCESS! All French email notifications are configured correctly!")
        print("\n📧 What will happen now:")
        print("   • All emails will be sent in French by default")
        print("   • Subjects will be translated to French")
        print("   • French templates will be used automatically")
        print("   • Fallback to English if French template missing")
        return True
    else:
        print(f"\n⚠️ WARNING: {total - passed} test(s) failed!")
        print("   Please review the failed tests above.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
