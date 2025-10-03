#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check notification system status
"""

import os
import sys
from datetime import datetime

def check_env_vars():
    """Check environment variables"""
    print("=== Environment Variables ===")
    required_vars = [
        'LINE_CHANNEL_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET', 
        'GOOGLE_SPREADSHEET_ID',
        'GOOGLE_CREDENTIALS_JSON'
    ]
    
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ .env file loaded")
    except Exception as e:
        print(f"✗ Error loading .env: {e}")
        return
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'GOOGLE_CREDENTIALS_JSON':
                if 'your_project_id' in value:
                    print(f"✗ {var}: Contains placeholder values")
                else:
                    print(f"✓ {var}: Configured")
            elif var == 'GOOGLE_SPREADSHEET_ID':
                if 'your_google_spreadsheet_id' in value:
                    print(f"✗ {var}: Contains placeholder values")
                else:
                    print(f"✓ {var}: Configured")
            else:
                print(f"✓ {var}: Set (length: {len(value)})")
        else:
            print(f"✗ {var}: Not set")

def check_libraries():
    """Check if required libraries are available"""
    print("\n=== Required Libraries ===")
    libraries = [
        'flask',
        'apscheduler', 
        'pytz',
        'linebot',
        'gspread',
        'google.auth'
    ]
    
    for lib in libraries:
        try:
            __import__(lib)
            print(f"✓ {lib}: Available")
        except ImportError:
            print(f"✗ {lib}: Not available")

def check_notification_service():
    """Check notification service status"""
    print("\n=== Notification Service ===")
    try:
        # Import required modules
        from notifications.notification_service import NotificationService
        from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
        
        # Mock LINE Bot API (won't actually send messages)
        config = Configuration(access_token="dummy_token")
        api_client = ApiClient(config)
        line_bot_api = MessagingApi(api_client)
        
        # Create notification service
        notification_service = NotificationService(line_bot_api)
        
        print(f"✓ NotificationService created")
        print(f"✓ Scheduler timezone: {notification_service.scheduler.timezone}")
        print(f"✓ Scheduler jobs: {len(notification_service.scheduler.get_jobs())}")
        
        for job in notification_service.scheduler.get_jobs():
            print(f"  - {job.name} (next: {job.next_run_time})")
        
        # Don't actually start scheduler
        print("✓ NotificationService initialized successfully")
        
    except Exception as e:
        print(f"✗ Error with NotificationService: {e}")
        import traceback
        traceback.print_exc()

def check_sheets_connection():
    """Check Google Sheets connection"""
    print("\n=== Google Sheets Connection ===")
    try:
        from storage.sheets_repo import SheetsRepository
        repo = SheetsRepository()
        
        if repo.gc and repo.spreadsheet:
            print(f"✓ Connected to spreadsheet: {repo.spreadsheet.title}")
            worksheets = repo.spreadsheet.worksheets()
            print(f"✓ Worksheets found: {len(worksheets)}")
            for ws in worksheets:
                print(f"  - {ws.title}")
        else:
            print("✗ No connection to Google Sheets")
            
    except Exception as e:
        print(f"✗ Error connecting to Google Sheets: {e}")

def main():
    """Main function"""
    print("LINE Bot Notification System Status Check")
    print("="*50)
    
    check_env_vars()
    check_libraries() 
    check_notification_service()
    check_sheets_connection()
    
    print("\n=== Summary ===")
    print("If notifications are not working, check:")
    print("1. Google Sheets credentials are properly configured")
    print("2. Spreadsheet ID is correct")
    print("3. There are appointments in the sheets")
    print("4. Scheduler is running in production")

if __name__ == "__main__":
    main()