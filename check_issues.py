#!/usr/bin/env python
"""
Quick diagnostic script to check for common issues in the Medical Site project
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description} MISSING: {dirpath}")
        return False

def check_file_content(filepath, search_string, description):
    """Check if a file contains a specific string"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - NOT FOUND")
                return False
    except Exception as e:
        print(f"❌ Error reading {filepath}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Medical Site - Issue Diagnostic Tool")
    print("=" * 60)
    print()
    
    issues_found = 0
    
    # Check critical files
    print("📁 Checking Critical Files...")
    if not check_file_exists('chat/routing.py', 'Chat Routing'):
        issues_found += 1
    if not check_file_exists('chat/consumers.py', 'Chat Consumers'):
        issues_found += 1
    if not check_file_exists('chat/middleware.py', 'Chat Middleware'):
        issues_found += 1
    if not check_file_exists('main/settings.py', 'Django Settings'):
        issues_found += 1
    if not check_file_exists('main/asgi.py', 'ASGI Configuration'):
        issues_found += 1
    print()
    
    # Check directories
    print("📂 Checking Directories...")
    if not check_directory_exists('static', 'Static Directory'):
        issues_found += 1
    if not check_directory_exists('media', 'Media Directory'):
        issues_found += 1
    if not check_directory_exists('chat/templates/chat', 'Chat Templates'):
        issues_found += 1
    print()
    
    # Check configurations
    print("⚙️ Checking Configurations...")
    if not check_file_content('main/settings.py', 'chat.middleware.ChatAuthMiddleware', 
                              'Chat Middleware in MIDDLEWARE'):
        issues_found += 1
    if not check_file_content('main/settings.py', 'CHANNEL_LAYERS', 
                              'Channel Layers Configuration'):
        issues_found += 1
    if not check_file_content('main/settings.py', 'ASGI_APPLICATION', 
                              'ASGI Application Configuration'):
        issues_found += 1
    if not check_file_content('chat/routing.py', 'websocket_urlpatterns', 
                              'WebSocket URL Patterns'):
        issues_found += 1
    print()
    
    # Check environment
    print("🔐 Checking Environment...")
    if not check_file_exists('.env', 'Environment File'):
        print("⚠️  WARNING: .env file not found. Make sure to create it with:")
        print("   - SECRET_KEY")
        print("   - OPENAI_API_KEY")
        print("   - DID_API_KEY")
        print("   - STRIPE_SECRET_KEY")
        print("   - SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
        print("   - SOCIAL_AUTH_FACEBOOK_KEY")
        issues_found += 1
    print()
    
    # Summary
    print("=" * 60)
    if issues_found == 0:
        print("✅ All checks passed! No issues found.")
    else:
        print(f"⚠️  Found {issues_found} issue(s) that need attention.")
    print("=" * 60)
    print()
    
    # Recommendations
    print("📋 Next Steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py collectstatic")
    print("4. Start server: python manage.py runserver")
    print("5. Test chat functionality at: http://127.0.0.1:8000/chat/")
    print()

if __name__ == '__main__':
    main()
