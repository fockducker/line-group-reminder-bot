#!/usr/bin/env python3
"""
Google Sheets Headers Migration Script
สคริปต์สำหรับอัปเดท headers เก่าเป็นใหม่ในทุก worksheet

Usage:
    python migrate_headers.py --analyze     # วิเคราะห์ worksheet (ไม่แก้ไขอะไร)
    python migrate_headers.py --dry-run     # ดูการเปลี่ยนแปลงก่อน (ไม่แก้ไขจริง)
    python migrate_headers.py --execute     # รัน migration จริง
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import gspread
from google.oauth2.service_account import Credentials

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HeaderMigrator:
    """Migration class สำหรับอัปเดท Google Sheets headers"""
    
    # Headers mapping เก่า -> ใหม่
    OLD_HEADERS = [
        'id', 'group_id', 'datetime_iso', 'hospital', 'department',
        'doctor', 'note', 'location', 'lead_days', 'notified_flags',
        'created_at', 'updated_at'
    ]
    
    NEW_HEADERS = [
        'id', 'group_id', 'datetime_iso', 'location', 'building_floor_dept',
        'contact_person', 'phone_number', 'note', 'lead_days', 'notified_flags',
        'created_at', 'updated_at'
    ]
    
    FIELD_MAPPING = {
        'hospital': 'location',
        'department': 'building_floor_dept',
        'doctor': 'contact_person'
    }
    
    def __init__(self):
        """Initialize migrator with Google Sheets connection"""
        self.gc = None
        self.spreadsheet = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """เชื่อมต่อกับ Google Sheets API"""
        try:
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if not credentials_json:
                raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable not found!")
            
            logger.info(f"Found credentials JSON (length: {len(credentials_json)} chars)")
            
            # Parse JSON credentials
            creds_dict = json.loads(credentials_json)
            
            # สร้าง credentials object
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            
            # เชื่อมต่อ gspread
            self.gc = gspread.authorize(credentials)
            
            # เชื่อมต่อ spreadsheet
            spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
            if not spreadsheet_id:
                raise ValueError("GOOGLE_SPREADSHEET_ID environment variable not found!")
            
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            logger.info(f"Successfully connected to Google Sheets: {self.spreadsheet.title}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def analyze_worksheets(self) -> Dict[str, Dict]:
        """วิเคราะห์ worksheet ทั้งหมดเพื่อดูว่าอันไหนต้อง migrate"""
        analysis = {}
        
        try:
            worksheets = self.spreadsheet.worksheets()
            logger.info(f"Found {len(worksheets)} worksheets")
            
            for worksheet in worksheets:
                sheet_name = worksheet.title
                logger.info(f"Analyzing worksheet: {sheet_name}")
                
                try:
                    # อ่าน header row
                    headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
                    
                    if not headers:
                        analysis[sheet_name] = {
                            'status': 'empty',
                            'headers': [],
                            'row_count': 0,
                            'needs_migration': False
                        }
                        continue
                    
                    # ตรวจสอบว่าเป็น headers เก่าหรือใหม่
                    is_old_format = self._is_old_format(headers)
                    row_count = worksheet.row_count
                    data_rows = max(0, row_count - 1)  # ลบ header row
                    
                    analysis[sheet_name] = {
                        'status': 'old_format' if is_old_format else 'new_format',
                        'headers': headers,
                        'row_count': row_count,
                        'data_rows': data_rows,
                        'needs_migration': is_old_format
                    }
                    
                    logger.info(f"  Status: {analysis[sheet_name]['status']}")
                    logger.info(f"  Data rows: {data_rows}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing worksheet {sheet_name}: {e}")
                    analysis[sheet_name] = {
                        'status': 'error',
                        'error': str(e),
                        'needs_migration': False
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing worksheets: {e}")
            return {}
    
    def _is_old_format(self, headers: List[str]) -> bool:
        """ตรวจสอบว่า headers เป็นรูปแบบเก่าหรือไม่"""
        # เช็คว่ามี hospital, department, doctor หรือไม่
        old_fields = ['hospital', 'department', 'doctor']
        has_old_fields = any(field in headers for field in old_fields)
        
        # เช็คว่าไม่มี phone_number
        has_phone_number = 'phone_number' in headers
        
        return has_old_fields and not has_phone_number
    
    def migrate_worksheet(self, worksheet_name: str, dry_run: bool = True) -> bool:
        """Migrate worksheet หนึ่งอัน"""
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            logger.info(f"Migrating worksheet: {worksheet_name}")
            
            # อ่านข้อมูลทั้งหมด
            all_values = worksheet.get_all_values()
            if not all_values:
                logger.info(f"Worksheet {worksheet_name} is empty, skipping")
                return True
            
            headers = all_values[0]
            data_rows = all_values[1:]
            
            # ตรวจสอบว่าต้อง migrate หรือไม่
            if not self._is_old_format(headers):
                logger.info(f"Worksheet {worksheet_name} already in new format, skipping")
                return True
            
            logger.info(f"Old headers: {headers}")
            
            # สร้าง mapping สำหรับ column index
            old_to_new_mapping = self._create_column_mapping(headers)
            
            # แปลงข้อมูล
            new_data = []
            new_data.append(self.NEW_HEADERS)  # Headers ใหม่
            
            for row in data_rows:
                new_row = self._transform_row(row, old_to_new_mapping, headers)
                new_data.append(new_row)
            
            logger.info(f"New headers: {self.NEW_HEADERS}")
            logger.info(f"Transformed {len(data_rows)} data rows")
            
            if dry_run:
                logger.info("DRY RUN: Would update worksheet with new data")
                # แสดงตัวอย่างข้อมูลที่จะเปลี่ยน
                if len(new_data) > 1:
                    logger.info(f"Example new row: {new_data[1]}")
                return True
            else:
                # อัปเดทข้อมูลจริง
                logger.info("Updating worksheet with new data...")
                
                # Clear worksheet
                worksheet.clear()
                
                # เขียนข้อมูลใหม่
                worksheet.update('A1', new_data)
                
                logger.info(f"Successfully migrated worksheet: {worksheet_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error migrating worksheet {worksheet_name}: {e}")
            return False
    
    def _create_column_mapping(self, old_headers: List[str]) -> Dict[str, int]:
        """สร้าง mapping ของ column index"""
        mapping = {}
        for i, header in enumerate(old_headers):
            mapping[header] = i
        return mapping
    
    def _transform_row(self, old_row: List[str], mapping: Dict[str, int], old_headers: List[str]) -> List[str]:
        """แปลงแถวข้อมูลจากรูปแบบเก่าเป็นใหม่"""
        new_row = [''] * len(self.NEW_HEADERS)
        
        for i, new_header in enumerate(self.NEW_HEADERS):
            if new_header == 'phone_number':
                # เพิ่ม phone_number ว่าง
                new_row[i] = ''
            elif new_header in self.FIELD_MAPPING.values():
                # หา field เก่าที่ map กับ field ใหม่
                old_field = None
                for old, new in self.FIELD_MAPPING.items():
                    if new == new_header:
                        old_field = old
                        break
                
                if old_field and old_field in mapping:
                    old_index = mapping[old_field]
                    if old_index < len(old_row):
                        new_row[i] = old_row[old_index]
            else:
                # Field ที่ไม่เปลี่ยนชื่อ
                if new_header in mapping:
                    old_index = mapping[new_header]
                    if old_index < len(old_row):
                        new_row[i] = old_row[old_index]
        
        return new_row
    
    def migrate_all(self, dry_run: bool = True) -> Dict[str, bool]:
        """Migrate ทุก worksheet"""
        logger.info(f"Starting migration (dry_run={dry_run})")
        
        # วิเคราะห์ worksheet ก่อน
        analysis = self.analyze_worksheets()
        
        # หา worksheet ที่ต้อง migrate
        worksheets_to_migrate = [
            name for name, info in analysis.items()
            if info.get('needs_migration', False)
        ]
        
        if not worksheets_to_migrate:
            logger.info("No worksheets need migration")
            return {}
        
        logger.info(f"Worksheets to migrate: {worksheets_to_migrate}")
        
        results = {}
        for worksheet_name in worksheets_to_migrate:
            logger.info(f"Processing: {worksheet_name}")
            success = self.migrate_worksheet(worksheet_name, dry_run)
            results[worksheet_name] = success
            
            if success:
                logger.info(f"✅ {worksheet_name}: Success")
            else:
                logger.error(f"❌ {worksheet_name}: Failed")
        
        return results


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Migrate Google Sheets headers')
    parser.add_argument('--analyze', action='store_true',
                       help='Only analyze worksheets and show status')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making actual changes')
    parser.add_argument('--execute', action='store_true',
                       help='Actually perform the migration')
    
    args = parser.parse_args()
    
    if not any([args.analyze, args.dry_run, args.execute]):
        print("Please specify one of: --analyze, --dry-run, or --execute")
        print("\nUsage:")
        print("  python migrate_headers.py --analyze     # วิเคราะห์ worksheet")
        print("  python migrate_headers.py --dry-run     # ดูการเปลี่ยนแปลงก่อน")
        print("  python migrate_headers.py --execute     # รัน migration จริง")
        sys.exit(1)
    
    try:
        migrator = HeaderMigrator()
        
        if args.analyze:
            logger.info("Analyzing worksheets...")
            analysis = migrator.analyze_worksheets()
            
            print("\n📊 WORKSHEET ANALYSIS:")
            print("=" * 60)
            for name, info in analysis.items():
                status = info.get('status', 'unknown')
                needs_migration = info.get('needs_migration', False)
                data_rows = info.get('data_rows', 0)
                
                print(f"📄 {name}")
                print(f"   Status: {status}")
                print(f"   Data rows: {data_rows}")
                print(f"   Needs migration: {'Yes' if needs_migration else 'No'}")
                
                if 'headers' in info and info['headers']:
                    print(f"   Headers: {info['headers']}")
                print()
        
        elif args.dry_run:
            logger.info("Running dry-run migration...")
            results = migrator.migrate_all(dry_run=True)
            
            print("\n🧪 DRY RUN RESULTS:")
            print("=" * 60)
            if not results:
                print("No worksheets need migration.")
            else:
                for worksheet, success in results.items():
                    status = "✅ Would succeed" if success else "❌ Would fail"
                    print(f"{status}: {worksheet}")
        
        elif args.execute:
            print("⚠️  WARNING: This will modify your Google Sheets data!")
            print("Make sure you have a backup before proceeding.")
            print("\nThis operation will:")
            print("  - Update headers from old format to new format")
            print("  - Add phone_number column with empty values")
            print("  - Rearrange data according to new column order")
            print()
            confirm = input("Type 'YES' to continue: ")
            
            if confirm != 'YES':
                print("Migration cancelled.")
                sys.exit(0)
            
            logger.info("Executing migration...")
            results = migrator.migrate_all(dry_run=False)
            
            print("\n🚀 MIGRATION RESULTS:")
            print("=" * 60)
            
            if not results:
                print("No worksheets needed migration.")
            else:
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                for worksheet, success in results.items():
                    status = "✅ Success" if success else "❌ Failed"
                    print(f"{status}: {worksheet}")
                
                print(f"\nSummary: {success_count}/{total_count} worksheets migrated successfully")
                
                if success_count == total_count and total_count > 0:
                    print("🎉 Migration completed successfully!")
                elif success_count > 0:
                    print("⚠️  Migration partially successful. Check logs for details.")
                else:
                    print("❌ Migration failed. Check logs for details.")
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()