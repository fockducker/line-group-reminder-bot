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
        logger.info("Starting daily notification check...")
        
        try:
            # ดึงการนัดหมายทั้งหมดจาก Google Sheets
            all_appointments = self._get_all_appointments()
            
            if not all_appointments:
                logger.info("No appointments found for notification")
                return
            
            notifications_sent = 0
            now = datetime.now(BANGKOK_TZ)
            
            for appointment in all_appointments:
                try:
                    # ส่งการแจ้งเตือนทุกนัดหมายทุกวัน
                    self._send_daily_notification(appointment, now)
                    notifications_sent += 1
                    
                except Exception as e:
                    logger.error(f"Error sending notification for appointment {appointment.id}: {e}")
            
            logger.info(f"Daily notification check completed. Sent {notifications_sent} notifications")
            
        except Exception as e:
            logger.error(f"Error in daily notification check: {e}", exc_info=True)
    
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
            
            # TODO: ดึงการนัดหมาย Group - ต้องมีวิธีการหา group_id ทั้งหมด
            # ปัจจุบันไม่มีวิธีการ list ทุก group ที่มีการนัดหมาย
            # อาจต้องเก็บ list ของ active groups หรือ scan worksheets
            
            logger.info(f"Retrieved total {len(all_appointments)} appointments for notification check")
            return all_appointments
            
        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return []
    
    def _should_notify_7_days(self, appointment_date: datetime, seven_days_later: datetime, appointment: Appointment) -> bool:
        """ตรวจสอบว่าควรแจ้งเตือน 7 วันก่อนหรือไม่"""
        # เช็คว่าการนัดหมายจะถึงในอีก 7 วัน (±6 ชั่วโมง)
        date_diff = abs((appointment_date.date() - seven_days_later.date()).days)
        
        # เช็คว่ายังไม่เคยส่งการแจ้งเตือน 7 วันก่อน
        not_notified_7_days = True
        if len(appointment.notified_flags) >= 1:
            not_notified_7_days = not appointment.notified_flags[0]  # index 0 = 7 days
        
        return date_diff == 0 and not_notified_7_days
    
    def _should_notify_1_day(self, appointment_date: datetime, one_day_later: datetime, appointment: Appointment) -> bool:
        """ตรวจสอบว่าควรแจ้งเตือน 1 วันก่อนหรือไม่"""
        # เช็คว่าการนัดหมายจะถึงพรุ่งนี้
        date_diff = abs((appointment_date.date() - one_day_later.date()).days)
        
        # เช็คว่ายังไม่เคยส่งการแจ้งเตือน 1 วันก่อน
        not_notified_1_day = True
        if len(appointment.notified_flags) >= 2:
            not_notified_1_day = not appointment.notified_flags[1]  # index 1 = 1 day
        
        return date_diff == 0 and not_notified_1_day
    
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
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=appointment.group_id,
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"Sent daily notification for appointment {appointment.id} to {appointment.group_id} (days_diff: {days_diff})")
            
        except Exception as e:
            logger.error(f"Failed to send daily notification for appointment {appointment.id}: {e}")

    def _send_7_day_notification(self, appointment: Appointment):
        """ส่งการแจ้งเตือน 7 วันก่อน"""
        try:
            message = f"""🗓️ การแจ้งเตือนล่วงหน้า

📅 คุณมีนัดหมายในอีก 1 สัปดาห์
🏥 {appointment.note}

⏰ วันที่: {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}
🏢 สถานที่: {appointment.hospital}
🔖 แผนก: {appointment.department}

💡 เตรียมตัวให้พร้อมนะคะ"""
            
            # ส่งข้อความแจ้งเตือนไปยังผู้ใช้
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=appointment.group_id,  # ส่งให้ user ที่เป็นเจ้าของนัดหมาย
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"Sent 7-day notification for appointment {appointment.id} to user {appointment.group_id}")
            
        except Exception as e:
            logger.error(f"Failed to send 7-day notification for appointment {appointment.id}: {e}")
    
    def _send_1_day_notification(self, appointment: Appointment):
        """ส่งการแจ้งเตือน 1 วันก่อน"""
        try:
            message = f"""⏰ แจ้งเตือนนัดหมาย!

🚨 พรุ่งนี้คุณมีนัดหมาย
🏥 {appointment.note}

📅 วันที่: {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}
🏢 สถานที่: {appointment.hospital}
🔖 แผนก: {appointment.department}
📍 สถานที่: {appointment.location}

✅ อย่าลืมเตรียมเอกสาร
✅ ไปให้ทันเวลา
✅ โทรยืนยันก่อนไปถ้าจำเป็น"""
            
            # ส่งข้อความแจ้งเตือนไปยังผู้ใช้
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=appointment.group_id,  # ส่งให้ user ที่เป็นเจ้าของนัดหมาย
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"Sent 1-day notification for appointment {appointment.id} to user {appointment.group_id}")
            
        except Exception as e:
            logger.error(f"Failed to send 1-day notification for appointment {appointment.id}: {e}")
    
    def _mark_notification_sent(self, appointment: Appointment, days_before: int):
        """อัปเดตสถานะการแจ้งเตือนใน Google Sheets"""
        try:
            # กำหนด context สำหรับ update
            if appointment.group_id.startswith('C'):  # Group ID
                context = f"group_{appointment.group_id}"
            else:  # Personal (User ID)
                context = "personal"
            
            # อัปเดต notified_flags
            updated_flags = appointment.notified_flags.copy() if appointment.notified_flags else [False, False, False]
            
            # ตาม lead_days [7, 3, 1] โดย 7=index 0, 3=index 1, 1=index 2
            if days_before == 7 and len(updated_flags) >= 1:
                updated_flags[0] = True  # 7 วันก่อน
            elif days_before == 3 and len(updated_flags) >= 2:
                updated_flags[1] = True  # 3 วันก่อน  
            elif days_before == 1 and len(updated_flags) >= 3:
                updated_flags[2] = True  # 1 วันก่อน
            
            # อัปเดตใน Google Sheets
            update_data = {
                'notified_flags': str(updated_flags)  # Convert to string for Sheets
            }
            
            success = self.sheets_repo.update_appointment(appointment.id, context, update_data)
            
            if success:
                logger.info(f"Marked {days_before}-day notification as sent for appointment {appointment.id}")
            else:
                logger.error(f"Failed to mark {days_before}-day notification as sent for appointment {appointment.id}")
            
        except Exception as e:
            logger.error(f"Failed to mark notification as sent: {e}")
    
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