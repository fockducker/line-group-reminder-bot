#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Google Sheets connection like handlers do
"""

import os
import sys
from datetime import datetime
import pytz

def load_env():
    """Load environment variables"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ .env file loaded")
        return True
    except Exception as e:
        print(f"✗ Error loading .env: {e}")
        return False

def test_sheets_like_handlers():
    """Test Google Sheets connection exactly like handlers do"""
    print("=== Testing Google Sheets (Handler Style) ===")
    
    try:
        from storage.sheets_repo import SheetsRepository
        
        # Create repo like handlers do
        repo = SheetsRepository()
        print(f"✓ SheetsRepository created")
        
        # Test personal appointments (like handlers)
        print("\n--- Personal Appointments ---")
        try:
            personal_appointments = repo.get_appointments("", "personal")
            print(f"✓ Personal appointments: {len(personal_appointments)}")
            for apt in personal_appointments:
                print(f"  - {apt.id}: {apt.note} ({apt.appointment_datetime})")
        except Exception as e:
            print(f"✗ Error getting personal appointments: {e}")
        
        # Test group appointments (find groups like handlers might)
        print("\n--- Group Appointments ---")
        if repo.gc and repo.spreadsheet:
            worksheets = repo.spreadsheet.worksheets()
            print(f"✓ Found {len(worksheets)} worksheets")
            
            for ws in worksheets:
                print(f"  - Worksheet: {ws.title}")
                if ws.title.startswith("group_"):
                    group_id = ws.title.replace("group_", "")
                    try:
                        group_appointments = repo.get_appointments(group_id, ws.title)
                        print(f"    → {len(group_appointments)} appointments")
                        for apt in group_appointments:
                            print(f"      • {apt.id}: {apt.note} ({apt.appointment_datetime})")
                    except Exception as e:
                        print(f"    → Error: {e}")
        else:
            print("✗ No Google Sheets connection")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_notifications_style():
    """Test Google Sheets connection like notification service does"""
    print("\n=== Testing Google Sheets (Notification Style) ===")
    
    try:
        from notifications.notification_service import NotificationService
        from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
        
        # Mock LINE Bot API
        config = Configuration(access_token="dummy_token")
        api_client = ApiClient(config)
        line_bot_api = MessagingApi(api_client)
        
        # Create notification service
        notification_service = NotificationService(line_bot_api)
        
        # Test _get_all_appointments like notification service does
        print("\n--- All Appointments (Notification Style) ---")
        all_appointments = notification_service._get_all_appointments()
        print(f"✓ Total appointments: {len(all_appointments)}")
        
        for apt in all_appointments:
            print(f"  - {apt.id}: {apt.note} ({apt.appointment_datetime}) [Group: {apt.group_id}]")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_manual_notification():
    """Test manual notification check"""
    print("\n=== Testing Manual Notification Check ===")
    
    try:
        from notifications.notification_service import NotificationService
        from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
        
        # Mock LINE Bot API
        config = Configuration(access_token="dummy_token")
        api_client = ApiClient(config)
        line_bot_api = MessagingApi(api_client)
        
        # Create notification service
        notification_service = NotificationService(line_bot_api)
        
        # Run check manually (but don't actually send notifications)
        print("✓ Calling check_and_send_notifications()...")
        
        # We'll simulate the check without sending actual messages
        all_appointments = notification_service._get_all_appointments()
        print(f"✓ Found {len(all_appointments)} appointments to check")
        
        if all_appointments:
            print("✓ Notification check would run successfully")
            print("  (Actual notifications would be sent to LINE)")
        else:
            print("✗ No appointments found - no notifications to send")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Google Sheets Connection Test")
    print("="*50)
    
    if not load_env():
        return
    
    test_sheets_like_handlers()
    test_notifications_style() 
    test_manual_notification()
    
    print("\n=== Analysis ===")
    print("If handlers can get data but notifications can't:")
    print("1. Check if both use same SheetsRepository initialization")
    print("2. Check if notification service has additional filtering")
    print("3. Check if there are environment differences")
    print("4. Check scheduler timing and error handling")

if __name__ == "__main__":
    main()