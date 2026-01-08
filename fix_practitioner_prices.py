#!/usr/bin/env python
"""
Fix practitioner prices - set default price for practitioners without one
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from user_account.models import Practitioner
from decimal import Decimal

def fix_practitioner_prices():
    """Set default prices for practitioners who don't have one"""
    print("🏥 Fixing Practitioner Prices...")
    
    # Find practitioners without prices
    practitioners_without_price = Practitioner.objects.filter(price__isnull=True)
    
    print(f"Found {practitioners_without_price.count()} practitioners without prices")
    
    if practitioners_without_price.count() == 0:
        print("✅ All practitioners already have prices set!")
        return
    
    # Set default price
    default_price = Decimal('50.00')  # $50 default consultation fee
    
    updated_count = 0
    for practitioner in practitioners_without_price:
        practitioner.price = default_price
        practitioner.save()
        updated_count += 1
        print(f"✅ Set price ${default_price} for Dr. {practitioner.first_name} {practitioner.last_name}")
    
    print(f"\n🎉 Updated {updated_count} practitioners with default price of ${default_price}")

def show_all_practitioner_prices():
    """Show all practitioner prices"""
    print("\n📊 Current Practitioner Prices:")
    print("=" * 50)
    
    practitioners = Practitioner.objects.all()
    
    for practitioner in practitioners:
        price_display = f"${practitioner.price}" if practitioner.price else "No price set"
        print(f"Dr. {practitioner.first_name} {practitioner.last_name}: {price_display}")

def main():
    """Main function"""
    print("🏥 Practitioner Price Fixer")
    print("=" * 30)
    
    # Show current prices
    show_all_practitioner_prices()
    
    # Fix missing prices
    fix_practitioner_prices()
    
    # Show updated prices
    show_all_practitioner_prices()

if __name__ == "__main__":
    main()