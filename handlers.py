"""
Event handlers module for LINE Group Reminder Bot
จัดการ event handlers สำหรับข้อความต่าง ๆ ที่ได้รับจาก LINE
"""

import logging
import uuid
from datetime import datetime, timedelta
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from storage.models import Appointment
from storage.sheets_repo import SheetsRepository

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_handlers(handler, line_bot_api):
    """
    ลงทะเบียน event handlers ทั้งหมดสำหรับ LINE Bot
    
    Args:
        handler: WebhookHandler instance
        line_bot_api: MessagingApi instance
    """
    logger.info("Registering LINE event handlers...")
    
    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_text_message(event):
        """จัดการข้อความที่เป็นข้อความธรรมดา"""
        user_message = event.message.text
        user_id = event.source.user_id
        
        # ตรวจสอบ context: 1:1 chat หรือ group chat
        if hasattr(event.source, 'group_id'):
            # Group Chat - ข้อมูลรวมกัน
            context_type = "group"
            context_id = event.source.group_id
            logger.info(f"Group message from {user_id} in group {context_id}: {user_message}")
        else:
            # 1:1 Chat - ข้อมูลส่วนตัว
            context_type = "personal" 
            context_id = user_id
            logger.info(f"Personal message from {user_id}: {user_message}")
        
        # จัดการข้อความและคำสั่งต่าง ๆ
        message_lower = user_message.lower().strip()
        
        # คำสั่งทักทาย
        if message_lower in ['hello', 'สวัสดี', 'ทักทาย']:
            if context_type == "group":
                reply_message = 'สวัสดี! ยินดีต้อนรับสู่ LINE Group Reminder Bot\\nนี่คือกลุ่มสำหรับจัดการการนัดหมายร่วมกัน\\n\\nพิมพ์ "คำสั่ง" เพื่อดูวิธีใช้งาน'
            else:
                reply_message = 'สวัสดี! ยินดีต้อนรับสู่ LINE Group Reminder Bot\\nนี่คือการนัดหมายส่วนตัวของคุณ\\n\\nพิมพ์ "คำสั่ง" เพื่อดูวิธีใช้งาน'
        
        # คำสั่งความช่วยเหลือ (Thai language commands)
        elif message_lower in ['help', 'คำสั่ง', 'ช่วยเหลือ', 'วิธีใช้']:
            base_help = 'คำสั่งการจัดการนัดหมาย:\\n"เพิ่มนัด" - เพิ่มการนัดหมายใหม่\\n"ดูนัด" - ดูรายการนัดหมาย\\n"ลบนัด" - ลบการนัดหมาย\\n"แก้ไขนัด" - แก้ไขการนัดหมาย\\n"สถานะ" - ดูสถานะของบอท\\n"เตือน" - ดูข้อมูลการแจ้งเตือน'
            
            if context_type == "group":
                reply_message = base_help + '\\n\\nโหมดกลุ่ม: การนัดหมายจะแสดงให้ทุกคนในกลุ่มเห็น'
            else:
                reply_message = base_help + '\\n\\nโหมดส่วนตัว: การนัดหมายของคุณเท่านั้น'
        
        # คำสั่งเพิ่มการนัดหมาย (รองรับแบบยืดหยุ่น)
        elif message_lower.startswith(('เพิ่มนัด', 'นัดใหม่', 'เพิ่มการนัด')):
            reply_message = handle_add_appointment_command(user_message, user_id, context_type, context_id)
        
        # คำสั่งดูการนัดหมาย
        elif message_lower in ['ดูนัด', 'รายการนัด', 'นัดหมาย', 'ดูการนัด']:
            reply_message = handle_list_appointments_command(user_id, context_type, context_id)
        
        # คำสั่งลบการนัดหมาย (รองรับแบบยืดหยุ่น)
        elif message_lower.startswith(('ลบนัด', 'ยกเลิกนัด', 'ลบการนัด')):
            reply_message = handle_delete_appointment_command(user_message, user_id, context_type, context_id)
        
        # คำสั่งแก้ไขการนัดหมาย (รองรับแบบยืดหยุ่น)
        elif message_lower.startswith(('แก้ไขนัด', 'แก้นัด', 'แก้ไขการนัด')):
            reply_message = handle_edit_appointment_command(user_message, user_id, context_type, context_id)
                
        elif message_lower == 'reminder':
            if context_type == "group":
                reply_message = 'การแจ้งเตือนกลุ่ม:\\nการนัดหมายในกลุ่มนี้จะแสดงให้ทุกคนเห็น\\nทุกคนสามารถเพิ่มการนัดหมายได้\\nการแจ้งเตือนจะส่งให้ทั้งกลุ่ม\\nระบบจะพัฒนาในอนาคต'
            else:
                reply_message = 'การแจ้งเตือนส่วนตัว:\\nการนัดหมายของคุณเป็นส่วนตัว\\nคนอื่นจะไม่เห็นข้อมูลของคุณ\\nการแจ้งเตือนส่งให้คุณเท่านั้น\\nระบบจะพัฒนาในอนาคต'
                
        elif message_lower == 'status':
            reply_message = f'สถานะของบอท:\\nเชื่อมต่อ LINE API สำเร็จ\\nรับข้อความได้ปกติ\\nส่งข้อความตอบกลับได้ปกติ\\nระบบ Scheduler พร้อมใช้งาน\\nContext: {context_type} ({context_id[:10]}...)'
        else:
            reply_message = f'คุณพิมพ์: "{user_message}"\\n\\nพิมพ์ "help" เพื่อดูคำสั่งที่ใช้ได้\\nContext: {context_type.title()}'
        
        # ส่งข้อความตอบกลับ
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )
            logger.info(f"Reply sent successfully: {reply_message[:50]}...")
        except Exception as e:
            logger.error(f"Failed to send reply: {e}")
    
    logger.info("LINE event handlers registered successfully")


def handle_add_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """
    จัดการคำสั่งเพิ่มการนัดหมาย
    รองรับการพิมพ์แบบยืดหยุ่น (flexible input)
    """
    try:
        # ตรวจสอบว่ามีข้อมูลเพิ่มเติมหรือไม่
        parts = user_message.strip().split()
        
        # ถ้าพิมพ์แค่ "เพิ่มนัด" ให้แสดงคำแนะนำ
        if len(parts) <= 1:
            return """การเพิ่มนัดหมายใหม่

วิธีใช้งาน:

แบบเต็ม:
เพิ่มนัด ตรวจสุขภาพประจำปี 2025-01-15 09:00 โรงพยาบาลราชวิถี

แบบง่าย:
เพิ่มนัด พบแพทย์ 15/1/25 เช้า

แบบสั้น:
เพิ่มนัด นัดหมอ พรุ่งนี้

พิมพ์อะไรไปก็ได้! บอทจะช่วยจัดการให้"""
        
        # ถ้ามีข้อมูลเพิ่มเติม ให้ทำการประมวลผลและบันทึกจริง
        else:
            appointment_text = " ".join(parts[1:])  # ข้อความหลัง "เพิ่มนัด"
            
            # กำหนด context สำหรับ Google Sheets
            if context_type == "group":
                sheets_context = f"group_{context_id}"
                group_id_for_model = context_id
            else:
                sheets_context = "personal"  
                group_id_for_model = user_id  # ใช้ user_id สำหรับ personal
            
            # สร้างการนัดหมายใหม่ (ใช้วันเวลาปัจจุบัน + 1 วันเป็นค่าเริ่มต้น)
            appointment_datetime = datetime.now() + timedelta(days=1)  # พรุ่งนี้
            
            appointment = Appointment(
                id=str(uuid.uuid4())[:8],  # สร้าง ID สั้น ๆ
                group_id=group_id_for_model,
                datetime_iso=appointment_datetime.isoformat(),
                hospital="LINE Bot",
                department="General",
                note=appointment_text,
                location="ระบุเพิ่มเติมภายหลัง"
            )
            
            logger.info(f"Created appointment: {appointment.to_dict()}")
            
            # บันทึกลง Google Sheets
            try:
                logger.info(f"Attempting to save appointment with context: {sheets_context}")
                logger.info(f"Appointment data: {appointment.to_dict()}")
                
                repo = SheetsRepository()
                logger.info(f"SheetsRepository created successfully. Connected: {repo.gc is not None}")
                logger.info(f"Spreadsheet available: {repo.spreadsheet is not None}")
                
                success = repo.add_appointment(appointment)
                logger.info(f"Add appointment result: {success}")
                
                if success:
                    return f"""✅ บันทึกนัดหมายสำเร็จ!

📝 ชื่อนัดหมาย: "{appointment_text}"
🆔 รหัส: {appointment.id}
📅 วันที่: {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}
📍 บริบท: {context_type}

✨ ข้อมูลถูกบันทึกใน Google Sheets แล้ว
💡 พิมพ์ "ดูนัด" เพื่อดูรายการทั้งหมด"""
                else:
                    logger.warning("Failed to save appointment - returned False")
                    return f"""⚠️ บันทึกนัดหมายไม่สำเร็จ

📝 ข้อมูล: "{appointment_text}"
❌ ไม่สามารถเชื่อมต่อ Google Sheets

🔧 กรุณาตรวจสอบการตั้งค่า Google Sheets
💡 หรือลองใหม่อีกครั้ง"""
                    
            except Exception as e:
                logger.error(f"Error saving appointment: {e}", exc_info=True)
                return f"""❌ เกิดข้อผิดพลาดในการบันทึก

📝 ข้อมูล: "{appointment_text}"
🔍 ข้อผิดพลาด: {str(e)}

💡 กรุณาตรวจสอบการตั้งค่า Google Sheets
🔧 ดู logs ใน Render Dashboard สำหรับรายละเอียด"""
        
    except Exception as e:
        logger.error(f"Error in handle_add_appointment_command: {e}")
        return "เกิดข้อผิดพลาดในการเพิ่มนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_list_appointments_command(user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งดูรายการนัดหมาย"""
    try:
        repo = SheetsRepository()
        
        # กำหนด context สำหรับ Google Sheets
        if context_type == "group":
            sheets_context = f"group_{context_id}"
        else:
            sheets_context = "personal"
        
        # ดึงรายการนัดหมาย
        appointments = repo.get_appointments(user_id, sheets_context)
        
        if not appointments:
            return """รายการนัดหมาย

ไม่พบการนัดหมายในขณะนี้

พิมพ์ "เพิ่มนัด" เพื่อเพิ่มการนัดหมายใหม่"""
        
        # สร้างรายการนัดหมาย
        appointment_list = "รายการนัดหมายของคุณ\\n\\n"
        
        for i, appointment in enumerate(appointments, 1):
            date_str = appointment.appointment_datetime.strftime("%d/%m/%Y %H:%M")
            appointment_list += f"{i}. {appointment.note}\\n"
            appointment_list += f"   วันที่: {date_str}\\n"
            if appointment.hospital and appointment.hospital != "LINE Bot":
                appointment_list += f"   โรงพยาบาล: {appointment.hospital}\\n"
            if appointment.department and appointment.department != "General":
                appointment_list += f"   แผนก: {appointment.department}\\n"
            appointment_list += f"   รหัส: {appointment.id}...\\n\\n"
        
        return appointment_list + "พิมพ์ 'ลบนัด [รหัส]' เพื่อลบการนัดหมาย"
        
    except Exception as e:
        logger.error(f"Error in handle_list_appointments_command: {e}")
        return "เกิดข้อผิดพลาดในการดึงข้อมูลนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_delete_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งลบการนัดหมาย"""
    try:
        return """การลบนัดหมาย

วิธีการใช้งาน:
ลบนัด [รหัสนัดหมาย]

ตัวอย่าง:
ลบนัด 12345678

ดูรหัสนัดหมายได้จากคำสั่ง "ดูนัด"

ฟีเจอร์นี้กำลังพัฒนา จะเสร็จเร็ว ๆ นี้!"""
        
    except Exception as e:
        logger.error(f"Error in handle_delete_appointment_command: {e}")
        return "เกิดข้อผิดพลาดในการลบนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_edit_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งแก้ไขการนัดหมาย"""
    try:
        return """การแก้ไขนัดหมาย

วิธีการใช้งาน:
แก้ไขนัด [รหัสนัดหมาย] [ข้อมูลใหม่]

ตัวอย่าง:
แก้ไขนัด 12345678 ชื่อใหม่: ตรวจสุขภาพ
แก้ไขนัด 12345678 วันที่: 2025-02-15

ดูรหัสนัดหมายได้จากคำสั่ง "ดูนัด"

ฟีเจอร์นี้กำลังพัฒนา จะเสร็จเร็ว ๆ นี้!"""
        
    except Exception as e:
        logger.error(f"Error in handle_edit_appointment_command: {e}")
        return "เกิดข้อผิดพลาดในการแก้ไขนัดหมาย กรุณาลองใหม่อีกครั้ง"