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
        self._notification_running = False  # ป้องกันการรันซ้ำ

        # Do NOT automatically register the job here. Registration is done when start_scheduler()
        # is explicitly called. This prevents multiple process instances from each scheduling
        # the same job (which causes duplicate notifications when the app is scaled).
        logger.info("NotificationService initialized (scheduler created, job not registered yet)")
    
    def start_scheduler(self):
        """เริ่มต้น background scheduler"""
        try:
            # Only start the scheduler if the environment explicitly allows it. This avoids
            # running the job in multiple processes when the app is scaled.
            import os
            start_flag = os.getenv('START_NOTIFICATION_SCHEDULER', 'false').lower()
            if start_flag not in ('1', 'true', 'yes'):
                logger.info("START_NOTIFICATION_SCHEDULER not enabled; scheduler will not start in this process")
                return

            # Register the daily job if not present
            existing_jobs = {j.id for j in self.scheduler.get_jobs()} if self.scheduler else set()
            if 'daily_notification_check' not in existing_jobs:
                self.scheduler.add_job(
                    func=self.check_and_send_notifications,
                    trigger=CronTrigger(hour=9, minute=0, timezone=BANGKOK_TZ),
                    id='daily_notification_check',
                    name='Daily Notification Check',
                    replace_existing=True,
                    max_instances=1
                )

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
        # ป้องกันการรันซ้ำ
        if self._notification_running:
            logger.warning("Notification check already running, skipping...")
            return
        
        self._notification_running = True
        
        try:
            logger.info("="*50)
            logger.info("Starting daily notification check...")
            logger.info(f"Current time: {datetime.now(BANGKOK_TZ)}")
            
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
            
            # เรียงลำดับนัดหมายจากใกล้ที่สุดไปไกลที่สุด
            now = datetime.now(BANGKOK_TZ)
            all_appointments.sort(key=lambda apt: apt.appointment_datetime)
            logger.info("Sorted appointments from nearest to farthest")
            
            # จัดกลุ่มนัดหมายตาม group_id/user_id
            appointments_by_recipient = {}
            for appointment in all_appointments:
                recipient_id = appointment.group_id
                if recipient_id not in appointments_by_recipient:
                    appointments_by_recipient[recipient_id] = []
                appointments_by_recipient[recipient_id].append(appointment)
            
            notifications_sent = 0
            
            # ส่งการแจ้งเตือนแยกตาม recipient
            for recipient_id, appointments in appointments_by_recipient.items():
                try:
                    self._send_daily_notification_summary(appointments, recipient_id, now)
                    notifications_sent += len(appointments)
                    logger.info(f"Notification summary sent to {recipient_id} for {len(appointments)} appointments")
                    
                except Exception as e:
                    logger.error(f"Error sending notification summary to {recipient_id}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            logger.info(f"Daily notification check completed. Sent {notifications_sent} notifications")
            
        except Exception as e:
            logger.error(f"Error in daily notification check: {e}", exc_info=True)
        finally:
            self._notification_running = False  # เสร็จแล้วปลดล็อก
    
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
            logger.info("Starting to retrieve all appointments...")
            
            # ดึงการนัดหมาย Personal
            try:
                logger.info("Attempting to retrieve personal appointments...")
                personal_appointments = self.sheets_repo.get_appointments("", "personal")
                if personal_appointments:
                    all_appointments.extend(personal_appointments)
                    logger.info(f"Retrieved {len(personal_appointments)} personal appointments")
                    # Debug: แสดงรายละเอียด personal appointments
                    for apt in personal_appointments:
                        logger.info(f"Personal appointment: {apt.id} - {apt.note} - User: {apt.group_id}")
                else:
                    logger.info("No personal appointments found")
            except Exception as e:
                logger.error(f"Error retrieving personal appointments: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
            # ดึงการนัดหมาย Group - หาอัตโนมัติจาก worksheets
            try:
                logger.info("Attempting to retrieve group appointments...")
                group_contexts = self._get_all_group_contexts()
                logger.info(f"Found {len(group_contexts)} group contexts")
                
                for group_info in group_contexts:
                    try:
                        group_appointments = self.sheets_repo.get_appointments(
                            group_info['group_id'], 
                            group_info['context']
                        )
                        if group_appointments:
                            all_appointments.extend(group_appointments)
                            logger.info(f"Retrieved {len(group_appointments)} appointments from {group_info['context']}")
                            # Debug: แสดงรายละเอียด group appointments
                            for apt in group_appointments:
                                logger.info(f"Group appointment: {apt.id} - {apt.note} - Group: {apt.group_id}")
                        else:
                            logger.info(f"No appointments found in {group_info['context']}")
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

📋 {appointment.note}
📅 วันที่: {appointment_date.strftime('%d/%m/%Y %H:%M')}
📍 สถานที่: {appointment.location}
🏢 อาคาร/แผนก/ชั้น: {appointment.building_floor_dept}"""
            
            if hasattr(appointment, 'contact_person') and appointment.contact_person:
                message += f"\n👤 บุคคล/ผู้ติดต่อ: {appointment.contact_person}"
            
            if hasattr(appointment, 'phone_number') and appointment.phone_number:
                message += f"\n📞 เบอร์โทร: {appointment.phone_number}"
            
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
            # Persist notified flag for this lead day if it exists in appointment.lead_days
            try:
                if isinstance(appointment.lead_days, list) and days_diff in appointment.lead_days:
                    idx = appointment.lead_days.index(days_diff)
                    # update in-memory and persist to Sheets
                    appointment.notified_flags[idx] = True
                    # Determine context for update
                    context = f"group_{appointment.group_id}" if appointment.group_id and appointment.group_id.startswith('C') else 'personal'
                    updated = {'notified_flags': str(appointment.notified_flags)}
                    try:
                        self.sheets_repo.update_appointment(appointment.id, context, updated)
                        logger.info(f"Persisted notified_flags for appointment {appointment.id} (lead_day={days_diff})")
                    except Exception as e:
                        logger.warning(f"Failed to persist notified_flags for {appointment.id}: {e}")
            except Exception:
                pass
            
        except Exception as e:
            logger.error(f"❌ Failed to send daily notification for appointment {appointment.id}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _send_daily_notification_summary(self, appointments: List[Appointment], recipient_id: str, current_time: datetime):
        """ส่งสรุปการแจ้งเตือนรายวันสำหรับหลายนัดหมาย เรียงจากใกล้ที่สุดไปไกลที่สุด"""
        try:
            if not appointments:
                return
            
            # สร้างหัวข้อข้อความ
            total_appointments = len(appointments)
            message = f"📋 สรุปนัดหมายประจำวัน ({total_appointments} รายการ)\n"
            message += f"🕘 {current_time.strftime('%d/%m/%Y %H:%M')}\n\n"
            
            # จัดกลุ่มนัดหมายตามความเร่งด่วน
            urgent_appointments = []      # วันนี้และพรุ่งนี้
            upcoming_appointments = []    # สัปดาห์นี้ (2-7 วัน)
            future_appointments = []      # อนาคต (>7 วัน)
            past_appointments = []        # ที่ผ่านแล้ว
            
            for appointment in appointments:
                appointment_date = appointment.appointment_datetime
                if appointment_date.tzinfo is None:
                    appointment_date = appointment_date.replace(tzinfo=BANGKOK_TZ)
                
                days_diff = (appointment_date.date() - current_time.date()).days
                
                if days_diff < 0:
                    past_appointments.append((appointment, days_diff))
                elif days_diff <= 1:
                    urgent_appointments.append((appointment, days_diff))
                elif days_diff <= 7:
                    upcoming_appointments.append((appointment, days_diff))
                else:
                    future_appointments.append((appointment, days_diff))
            
            # แสดงนัดหมายด่วน (วันนี้/พรุ่งนี้)
            if urgent_appointments:
                message += "🚨 นัดหมายด่วน:\n"
                for appointment, days_diff in urgent_appointments:
                    if days_diff == 0:
                        status_emoji = "🔥"
                        status_text = "วันนี้"
                    else:
                        status_emoji = "⚡"
                        status_text = "พรุ่งนี้"
                    
                    message += f"{status_emoji} {status_text} - {appointment.note}\n"
                    message += f"   📅 {appointment.appointment_datetime.strftime('%H:%M')}"
                    if appointment.location and appointment.location != "LINE Bot":
                        message += f" ที่ {appointment.location}"
                    if getattr(appointment, 'contact_person', None) and appointment.contact_person:
                        message += f" พบ {appointment.contact_person}"
                    message += f"\n   🆔 {appointment.id}\n\n"
            
            # แสดงนัดหมายสัปดาห์นี้
            if upcoming_appointments:
                message += "📅 สัปดาห์นี้:\n"
                for appointment, days_diff in upcoming_appointments:
                    message += f"🔴 ในอีก {days_diff} วัน - {appointment.note}\n"
                    message += f"   📅 {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}"
                    if appointment.location and appointment.location != "LINE Bot":
                        message += f" ที่ {appointment.location}"
                    message += f"\n   🆔 {appointment.id}\n\n"
            
            # แสดงนัดหมายในอนาคต (จำกัด 3 รายการแรก)
            if future_appointments:
                message += "🟡 นัดหมายถัดไป:\n"
                for appointment, days_diff in future_appointments[:3]:
                    message += f"📅 ในอีก {days_diff} วัน - {appointment.note}\n"
                    message += f"   📅 {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}"
                    if appointment.location and appointment.location != "LINE Bot":
                        message += f" ที่ {appointment.location}"
                    message += f"\n   🆔 {appointment.id}\n\n"
                
                if len(future_appointments) > 3:
                    message += f"   และอีก {len(future_appointments) - 3} นัดหมาย...\n\n"
            
            # แสดงนัดหมายที่ผ่านแล้ว (จำกัด 2 รายการล่าสุด)
            if past_appointments:
                message += "⚪ ที่ผ่านมา:\n"
                # เรียงจากล่าสุดก่อน
                past_appointments.sort(key=lambda x: x[1], reverse=True)
                for appointment, days_diff in past_appointments[:2]:
                    message += f"⏰ เมื่อ {abs(days_diff)} วันที่แล้ว - {appointment.note}\n"
                    message += f"   🆔 {appointment.id}\n\n"
            
            # เพิ่ม footer
            message += "💡 พิมพ์ 'ดูนัด' เพื่อดูรายละเอียดทั้งหมด\n"
            message += "🔔 ระบบแจ้งเตือนอัตโนมัติทุกวัน 09:00 น."
            
            # ส่งข้อความแจ้งเตือน
            logger.info(f"Sending daily summary to {recipient_id} for {total_appointments} appointments")
            logger.info(f"Summary preview: {message[:200]}...")
            
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=recipient_id,
                    messages=[TextMessage(text=message)]
                )
            )
            
            logger.info(f"✅ Sent daily notification summary to {recipient_id}")
            # Persist notified flags for appointments that match lead days
            try:
                for appointment in appointments:
                    try:
                        apt_date = appointment.appointment_datetime
                        if apt_date.tzinfo is None:
                            apt_date = apt_date.replace(tzinfo=BANGKOK_TZ)
                        days_diff = (apt_date.date() - current_time.date()).days
                        if isinstance(appointment.lead_days, list) and days_diff in appointment.lead_days:
                            idx = appointment.lead_days.index(days_diff)
                            appointment.notified_flags[idx] = True
                            context = f"group_{appointment.group_id}" if appointment.group_id and appointment.group_id.startswith('C') else 'personal'
                            updated = {'notified_flags': str(appointment.notified_flags)}
                            try:
                                self.sheets_repo.update_appointment(appointment.id, context, updated)
                                logger.info(f"Persisted notified_flags for appointment {appointment.id} after summary send (lead_day={days_diff})")
                            except Exception as e:
                                logger.warning(f"Failed to persist notified_flags (summary) for {appointment.id}: {e}")
                    except Exception:
                        continue
            except Exception:
                pass
            
        except Exception as e:
            logger.error(f"❌ Failed to send daily notification summary to {recipient_id}: {e}")
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