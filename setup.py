#!/usr/bin/env python
"""
Setup script for Stylette Django project
Run this script to set up the project for the first time
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Stylette Django E-commerce Project")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Please create it with your environment variables.")
        print("   See README.md for required environment variables.")
        return False
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stylette.settings')
    
    try:
        django.setup()
    except Exception as e:
        print(f"✗ Django setup failed: {e}")
        return False
    
    # Run Django commands
    commands = [
        ("python manage.py makemigrations", "Creating migrations"),
        ("python manage.py migrate", "Applying migrations"),
        ("python manage.py collectstatic --noinput", "Collecting static files"),
        ("python manage.py populate_data", "Populating with sample data"),
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
            break
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://127.0.0.1:8000")
        print("3. Admin panel: http://127.0.0.1:8000/admin/")
        print("   Username: admin")
        print("   Password: admin123")
        print("\nHappy coding! 🛍️")
    else:
        print("\n" + "=" * 50)
        print("❌ Setup failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    main()


