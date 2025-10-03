"""
Notification System for LINE Group Reminder Bot
จัดการระบบแจ้งเตือนอัตโนมัติสำหรับการนัดหมาย
"""

import logging
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from linebot.v3.messaging import MessagingApi, PushMessageRequest, TextMessage

from storage.sheets_repo import SheetsRepository
from storage.models import Appointment

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ตั้งค่า timezone สำหรับประเทศไทย
BANGKOK_TZ = pytz.timezone('Asia/Bangkok')


class NotificationService:
    """
    Service สำหรับจัดการการแจ้งเตือนการนัดหมาย
    รองรับการแจ้งเตือนล่วงหน้า 7 วัน และ 1 วัน
    """
    
    def __init__(self, line_bot_api: MessagingApi):
        """
        Initialize NotificationService
        
        Args:
            line_bot_api (MessagingApi): LINE Bot API instance
        """
        self.line_bot_api = line_bot_api
        self.scheduler = BackgroundScheduler(timezone=BANGKOK_TZ)
        self.sheets_repo = SheetsRepository()
        
        # ตั้งค่า scheduler ให้ทำงานทุกวันเวลา 09:00
        self.scheduler.add_job(
            func=self.check_and_send_notifications,
            trigger=CronTrigger(hour=9, minute=0, timezone=BANGKOK_TZ),
            id='daily_notification_check',
            name='Daily Notification Check',
            replace_existing=True
        )
        
        logger.info("NotificationService initialized with daily scheduler at 09:00 Bangkok time")
    
    def start_scheduler(self):
        """เริ่มต้น background scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Notification scheduler started successfully")
            else:
                logger.info("Notification scheduler is already running")
        except Exception as e:
            logger.error(f"Failed to start notification scheduler: {e}")
    
    def stop_scheduler(self):
        """หยุด background scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Notification scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop notification scheduler: {e}")
    
    def check_and_send_notifications(self):
        """
        ตรวจสอบการนัดหมายและส่งการแจ้งเตือน
        ฟังก์ชันนี้จะถูกเรียกทุกวันเวลา 09:00
        แจ้งเตือนทุกนัดหมายที่มีอยู่ทุกวัน
        """
        logger.info("="*50)
        logger.info("Starting daily notification check...")
        logger.info(f"Current time: {datetime.now(BANGKOK_TZ)}")
        
        try:
            # ตรวจสอบ Google Sheets connection
            if not self.sheets_repo.gc or not self.sheets_repo.spreadsheet:
                logger.error("Google Sheets not connected - cannot send notifications")
                return
            
            logger.info("Google Sheets connected successfully")
            
            # ดึงการนัดหมายทั้งหมดจาก Google Sheets
            all_appointments = self._get_all_appointments()
            
            if not all_appointments:
                logger.warning("No appointments found for notification")
                logger.info("Checked both personal and group contexts")
                return
            
            logger.info(f"Found {len(all_appointments)} appointments to process")
            notifications_sent = 0
            now = datetime.now(BANGKOK_TZ)
            
            for appointment in all_appointments:
                try:
                    logger.info(f"Processing appointment {appointment.id}: {appointment.note}")
                    # ส่งการแจ้งเตือนทุกนัดหมายทุกวัน
                    self._send_daily_notification(appointment, now)
                    notifications_sent += 1
                    logger.info(f"Notification sent successfully for {appointment.id}")
                    
                except Exception as e:
                    logger.error(f"Error sending notification for appointment {appointment.id}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            logger.info(f"Daily notification check completed. Sent {notifications_sent} notifications")
            
        except Exception as e:
            logger.error(f"Error in daily notification check: {e}", exc_info=True)
    
    def _get_all_group_contexts(self):
        """หา group contexts ทั้งหมดจาก Google Sheets worksheets"""
        try:
            # ดึงรายชื่อ worksheets ทั้งหมด
            if not self.sheets_repo.gc:
                return []
                
            spreadsheet = self.sheets_repo.spreadsheet
            if not spreadsheet:
                return []
            
            group_contexts = []
            worksheets = spreadsheet.worksheets()
            
            for worksheet in worksheets:
                worksheet_title = worksheet.title
                # หา worksheets ที่ขึ้นต้นด้วย "appointments_group_"
                if worksheet_title.startswith("appointments_group_"):
                    group_id = worksheet_title.replace("appointments_group_", "")
                    group_contexts.append({
                        'group_id': group_id,
                        'context': worksheet_title
                    })
                    logger.info(f"Found group context: {worksheet_title}")
                # เพิ่มการรองรับ format เก่า "group_" (ถ้ามี)
                elif worksheet_title.startswith("group_"):
                    group_id = worksheet_title.replace("group_", "")
                    group_contexts.append({
                        'group_id': group_id,
                        'context': worksheet_title
                    })
                    logger.info(f"Found group context (legacy): {worksheet_title}")
            
            logger.info(f"Total group contexts found: {len(group_contexts)}")
            return group_contexts
            
        except Exception as e:
            logger.error(f"Error getting group contexts: {e}")
            return []

    def _get_all_appointments(self) -> List[Appointment]:
        """ดึงการนัดหมายทั้งหมดจาก Google Sheets"""
        try:
            all_appointments = []
            
            # ดึงการนัดหมาย Personal
            try:
                personal_appointments = self.sheets_repo.get_appointments("", "personal")
                all_appointments.extend(personal_appointments)
                logger.info(f"Retrieved {len(personal_appointments)} personal appointments")
            except Exception as e:
                logger.error(f"Error retrieving personal appointments: {e}")
            
            # ดึงการนัดหมาย Group - หาอัตโนมัติจาก worksheets
            try:
                group_contexts = self._get_all_group_contexts()
                logger.info(f"Found {len(group_contexts)} group contexts")
                
                for group_info in group_contexts:
                    try:
                        group_appointments = self.sheets_repo.get_appointments(
                            group_info['group_id'], 
                            group_info['context']
                        )
                        all_appointments.extend(group_appointments)
                        logger.info(f"Retrieved {len(group_appointments)} appointments from {group_info['context']}")
                    except Exception as e:
                        logger.error(f"Error retrieving appointments from {group_info['context']}: {e}")
                        
            except Exception as e:
                logger.error(f"Error processing group appointments: {e}")
            
            logger.info(f"Retrieved total {len(all_appointments)} appointments for notification check")
            return all_appointments
            
        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return []
    


    
    def _send_daily_notification(self, appointment: Appointment, current_time: datetime):
        """ส่งการแจ้งเตือนรายวันสำหรับนัดหมาย"""
        try:
            # คำนวณจำนวนวันที่เหลือ
            appointment_date = appointment.appointment_datetime
            if appointment_date.tzinfo is None:
                appointment_date = appointment_date.replace(tzinfo=BANGKOK_TZ)
            
            days_diff = (appointment_date.date() - current_time.date()).days
            
            # กำหนดข้อความตามจำนวนวันที่เหลือ
            if days_diff < 0:
                # นัดหมายที่ผ่านไปแล้ว
                status_msg = f"⏰ นัดหมายที่ผ่านมาแล้ว {abs(days_diff)} วัน"
                status_emoji = "⚪"
            elif days_diff == 0:
                # นัดหมายวันนี้
                status_msg = "🔥 นัดหมายวันนี้!"
                status_emoji = "🔥"
            elif days_diff == 1:
                # นัดหมายพรุ่งนี้
                status_msg = "⚡ นัดหมายพรุ่งนี้!"
                status_emoji = "⚡"
            elif days_diff <= 7:
                # นัดหมายสัปดาห์นี้
                status_msg = f"🔴 นัดหมายในอีก {days_diff} วัน"
                status_emoji = "🔴"
            else:
                # นัดหมายในอนาคต
                status_msg = f"🟡 นัดหมายในอีก {days_diff} วัน"
                status_emoji = "🟡"
            
            message = f"""📋 สรุปนัดหมายประจำวัน

{status_emoji} {status_msg}

🏥 {appointment.note}
📅 วันที่: {appointment_date.strftime('%d/%m/%Y %H:%M')}
🏢 สถานที่: {appointment.hospital}
🔖 แผนก: {appointment.department}"""
            
            if hasattr(appointment, 'doctor') and appointment.doctor:
                message += f"\n👨‍⚕️ แพทย์: {appointment.doctor}"
            
            message += f"\n🆔 รหัส: {appointment.id}"
            
            # เพิ่มข้อความพิเศษตามวัน
            if days_diff == 0:
                message += "\n\n✅ อย่าลืมไปนัดหมายวันนี้!"
            elif days_diff == 1:
                message += "\n\n📝 เตรียมเอกสาร และไปให้ทันเวลา"
            elif days_diff > 0 and days_diff <= 7:
                message += f"\n\n⏰ เหลืออีก {days_diff} วัน อย่าลืมเตรียมตัว"
            
            # ส่งข้อความแจ้งเตือนไปยังผู้ใช้
            logger.info(f"Sending notification to {appointment.group_id} for appointment {appointment.id}")
            logger.info(f"Message preview: {message[:100]}...")
            
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=appointment.group_id,
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"✅ Sent daily notification for appointment {appointment.id} to {appointment.group_id} (days_diff: {days_diff})")
            
        except Exception as e:
            logger.error(f"❌ Failed to send daily notification for appointment {appointment.id}: {e}")
            import traceback
            logger.error(traceback.format_exc())




    
    def send_test_notification(self, user_id: str, message: str = None):
        """ส่งการแจ้งเตือนทดสอบ (สำหรับ debugging)"""
        try:
            test_message = message or f"""🧪 ทดสอบระบบแจ้งเตือน

✅ ระบบแจ้งเตือนทำงานปกติ
⏰ เวลาปัจจุบัน: {datetime.now(BANGKOK_TZ).strftime('%d/%m/%Y %H:%M:%S')}

📋 ระบบจะแจ้งเตือน:
• 🗓️ 7 วันก่อนนัดหมาย (09:00 น.)
• ⏰ 1 วันก่อนนัดหมาย (09:00 น.)"""
            
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=test_message)]
                )
            )
            
            logger.info(f"Sent test notification to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test notification to user {user_id}: {e}")
            return False
    
    def debug_notification_system(self):
        """Debug function สำหรับตรวจสอบระบบ notification"""
        logger.info("="*60)
        logger.info("🔍 NOTIFICATION SYSTEM DEBUG")
        logger.info("="*60)
        
        # 1. ตรวจสอบ Google Sheets connection
        logger.info("1. Google Sheets Connection:")
        if self.sheets_repo.gc and self.sheets_repo.spreadsheet:
            logger.info(f"   ✅ Connected to: {self.sheets_repo.spreadsheet.title}")
            worksheets = self.sheets_repo.spreadsheet.worksheets()
            logger.info(f"   ✅ Worksheets: {len(worksheets)}")
            for ws in worksheets:
                if ws.title.startswith("appointments_group_"):
                    logger.info(f"      - {ws.title} (GROUP WORKSHEET)")
                elif ws.title == "appointments_personal":
                    logger.info(f"      - {ws.title} (PERSONAL WORKSHEET)")
                else:
                    logger.info(f"      - {ws.title} (OTHER)")
        else:
            logger.error("   ❌ Google Sheets not connected")
            return
        
        # 1.5 ตรวจสอบ Group Contexts Detection
        logger.info("\n1.5. Group Contexts Detection:")
        group_contexts = self._get_all_group_contexts()
        logger.info(f"   📊 Group contexts detected: {len(group_contexts)}")
        for gc in group_contexts:
            logger.info(f"      - Group ID: {gc['group_id']}, Context: {gc['context']}")
        
        # 2. ตรวจสอบการนัดหมาย
        logger.info("\n2. Appointments Check:")
        all_appointments = self._get_all_appointments()
        logger.info(f"   📊 Total appointments: {len(all_appointments)}")
        
        if all_appointments:
            for apt in all_appointments:
                days_diff = (apt.appointment_datetime.date() - datetime.now(BANGKOK_TZ).date()).days
                logger.info(f"   📅 {apt.id}: {apt.note} (in {days_diff} days)")
        else:
            logger.warning("   ❌ No appointments found")
            return
        
        # 3. ตรวจสอบ Scheduler
        logger.info("\n3. Scheduler Status:")
        logger.info(f"   ⏰ Running: {self.scheduler.running}")
        logger.info(f"   🌍 Timezone: {self.scheduler.timezone}")
        jobs = self.scheduler.get_jobs()
        logger.info(f"   📋 Jobs: {len(jobs)}")
        for job in jobs:
            logger.info(f"      - {job.name} ({job.id})")
        
        logger.info("\n4. Test Summary:")
        if all_appointments and self.sheets_repo.gc:
            logger.info("   ✅ System ready for notifications")
            logger.info("   💡 Next check: 09:00 Bangkok time daily")
        else:
            logger.warning("   ❌ System not ready - missing data or connection")
        
        logger.info("="*60)