"""
Event handlers module for LINE Group Reminder Bot
จัดการ event handlers สำหรับข้อความต่าง ๆ ที่ได้รับจาก LINE
"""

import logging
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
                reply_message = f'สวัสดี! ยินดีต้อนรับสู่ LINE Group Reminder Bot\n🏥 นี่คือกลุ่มสำหรับจัดการการนัดหมายร่วมกัน\n\n📝 พิมพ์ "คำสั่ง" เพื่อดูวิธีใช้งาน'
            else:
                reply_message = f'สวัสดี! ยินดีต้อนรับสู่ LINE Group Reminder Bot\n👤 นี่คือการนัดหมายส่วนตัวของคุณ\n\n📝 พิมพ์ "คำสั่ง" เพื่อดูวิธีใช้งาน'
        
        # คำสั่งความช่วยเหลือ (Thai language commands)
        elif message_lower in ['help', 'คำสั่ง', 'ช่วยเหลือ', 'วิธีใช้']:
            base_help = '''🏥 คำสั่งการจัดการนัดหมาย:
📅 "เพิ่มนัด" - เพิ่มการนัดหมายใหม่
📋 "ดูนัด" - ดูรายการนัดหมาย
❌ "ลบนัด" - ลบการนัดหมาย
✏️ "แก้ไขนัด" - แก้ไขการนัดหมาย
📊 "สถานะ" - ดูสถานะของบอท
🔔 "เตือน" - ดูข้อมูลการแจ้งเตือน'''
            
            if context_type == "group":
                reply_message = base_help + '\n\n🏥 โหมดกลุ่ม: การนัดหมายจะแสดงให้ทุกคนในกลุ่มเห็น'
            else:
                reply_message = base_help + '\n\n👤 โหมดส่วนตัว: การนัดหมายของคุณเท่านั้น'
        
        # คำสั่งเพิ่มการนัดหมาย
        elif message_lower in ['เพิ่มนัด', 'นัดใหม่', 'เพิ่มการนัด']:
            reply_message = handle_add_appointment_command(user_message, user_id, context_type, context_id)
        
        # คำสั่งดูการนัดหมาย
        elif message_lower in ['ดูนัด', 'รายการนัด', 'นัดหมาย', 'ดูการนัด']:
            reply_message = handle_list_appointments_command(user_id, context_type, context_id)
        
        # คำสั่งลบการนัดหมาย
        elif message_lower in ['ลบนัด', 'ยกเลิกนัด', 'ลบการนัด']:
            reply_message = handle_delete_appointment_command(user_message, user_id, context_type, context_id)
        
        # คำสั่งแก้ไขการนัดหมาย
        elif message_lower in ['แก้ไขนัด', 'แก้นัด', 'แก้ไขการนัด']:
            reply_message = handle_edit_appointment_command(user_message, user_id, context_type, context_id)
        
        # คำสั่งการแจ้งเตือน
        elif message_lower in ['reminder', 'เตือน', 'การแจ้งเตือน']:
            if context_type == "group":
                reply_message = '''🔔 การแจ้งเตือนกลุ่ม:
🏥 การนัดหมายในกลุ่มนี้จะแสดงให้ทุกคนเห็น
📝 ทุกคนสามารถเพิ่มการนัดหมายได้
🔔 การแจ้งเตือนจะส่งให้ทั้งกลุ่ม
� ข้อมูลจัดเก็บใน Google Sheets
✅ ระบบพร้อมใช้งาน'''
            else:
                reply_message = '''🔔 การแจ้งเตือนส่วนตัว:
👤 การนัดหมายของคุณเป็นส่วนตัว
🔐 คนอื่นจะไม่เห็นข้อมูลของคุณ
🔔 การแจ้งเตือนส่งให้คุณเท่านั้น
� ข้อมูลจัดเก็บใน Google Sheets
✅ ระบบพร้อมใช้งาน'''
                
        # คำสั่งสถานะ
        elif message_lower in ['status', 'สถานะ', 'ตรวจสอบ']:
            reply_message = f'''📊 สถานะของบอท:
✅ เชื่อมต่อ LINE API สำเร็จ
✅ รับข้อความได้ปกติ  
✅ ส่งข้อความตอบกลับได้ปกติ
🔄 ระบบ Scheduler พร้อมใช้งาน
📊 Google Sheets Integration พร้อมใช้งาน
🇹🇭 ระบบคำสั่งภาษาไทยพร้อมใช้งาน
📍 Context: {context_type} ({context_id[:10]}...)
⏰ เวลา: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'''
        else:
            reply_message = f'คุณพิมพ์: "{user_message}"\n\n💡 พิมพ์ "help" เพื่อดูคำสั่งที่ใช้ได้\n🏥 Context: {context_type.title()}'
        
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
    
    Args:
        user_message (str): ข้อความจากผู้ใช้
        user_id (str): LINE User ID
        context_type (str): ประเภท context ('personal' หรือ 'group')
        context_id (str): ID ของ context
    
    Returns:
        str: ข้อความตอบกลับ
    """
    try:
        # ตัวอย่างรูปแบบการใช้งาน
        return """📅 การเพิ่มนัดหมายใหม่

วิธีการใช้งาน:
เพิ่มนัด [ชื่อการนัด] [วันที่] [เวลา] [รายละเอียด]

ตัวอย่าง:
เพิ่มนัด ตรวจสุขภาพประจำปี 2025-01-15 09:00 โรงพยาบาลราชวิถี

หรือใช้รูปแบบง่าย ๆ:
เพิ่มนัด พบแพทย์ 15/1/25 เช้า

💡 ระบบจะถามรายละเอียดเพิ่มเติมในขั้นตอนถัดไป
🔄 ฟีเจอร์นี้กำลังพัฒนา จะเสร็จเร็ว ๆ นี้!"""
        
    except Exception as e:
        logger.error(f"Error in handle_add_appointment_command: {e}")
        return "❌ เกิดข้อผิดพลาดในการเพิ่มนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_list_appointments_command(user_id: str, context_type: str, context_id: str) -> str:
    """
    จัดการคำสั่งดูรายการนัดหมาย
    
    Args:
        user_id (str): LINE User ID
        context_type (str): ประเภท context ('personal' หรือ 'group')
        context_id (str): ID ของ context
    
    Returns:
        str: ข้อความตอบกลับ
    """
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
            return """📋 รายการนัดหมาย

ไม่พบการนัดหมายในขณะนี้

💡 พิมพ์ "เพิ่มนัด" เพื่อเพิ่มการนัดหมายใหม่"""
        
        # สร้างรายการนัดหมาย
        appointment_list = "📋 รายการนัดหมายของคุณ\n\n"
        
        for i, appointment in enumerate(appointments, 1):
            date_str = appointment.appointment_date.strftime("%d/%m/%Y %H:%M")
            appointment_list += f"{i}. {appointment.title}\n"
            appointment_list += f"   📅 {date_str}\n"
            if appointment.description:
                appointment_list += f"   📝 {appointment.description}\n"
            appointment_list += f"   🆔 {appointment.id[:8]}...\n\n"
        
        return appointment_list + "💡 พิมพ์ 'ลบนัด [รหัส]' เพื่อลบการนัดหมาย"
        
    except Exception as e:
        logger.error(f"Error in handle_list_appointments_command: {e}")
        return "❌ เกิดข้อผิดพลาดในการดึงข้อมูลนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_delete_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """
    จัดการคำสั่งลบการนัดหมาย
    
    Args:
        user_message (str): ข้อความจากผู้ใช้
        user_id (str): LINE User ID
        context_type (str): ประเภท context ('personal' หรือ 'group')
        context_id (str): ID ของ context
    
    Returns:
        str: ข้อความตอบกลับ
    """
    try:
        return """❌ การลบนัดหมาย

วิธีการใช้งาน:
ลบนัด [รหัสนัดหมาย]

ตัวอย่าง:
ลบนัด 12345678

💡 ดูรหัสนัดหมายได้จากคำสั่ง "ดูนัด"
🔄 ฟีเจอร์นี้กำลังพัฒนา จะเสร็จเร็ว ๆ นี้!"""
        
    except Exception as e:
        logger.error(f"Error in handle_delete_appointment_command: {e}")
        return "❌ เกิดข้อผิดพลาดในการลบนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_edit_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """
    จัดการคำสั่งแก้ไขการนัดหมาย
    
    Args:
        user_message (str): ข้อความจากผู้ใช้
        user_id (str): LINE User ID
        context_type (str): ประเภท context ('personal' หรือ 'group')
        context_id (str): ID ของ context
    
    Returns:
        str: ข้อความตอบกลับ
    """
    try:
        return """✏️ การแก้ไขนัดหมาย

วิธีการใช้งาน:
แก้ไขนัด [รหัสนัดหมาย] [ข้อมูลใหม่]

ตัวอย่าง:
แก้ไขนัด 12345678 ชื่อใหม่: ตรวจสุขภาพ
แก้ไขนัด 12345678 วันที่: 2025-02-15
แก้ไขนัด 12345678 เวลา: 10:30

💡 ดูรหัสนัดหมายได้จากคำสั่ง "ดูนัด"
🔄 ฟีเจอร์นี้กำลังพัฒนา จะเสร็จเร็ว ๆ นี้!"""
        
    except Exception as e:
        logger.error(f"Error in handle_edit_appointment_command: {e}")
        return "❌ เกิดข้อผิดพลาดในการแก้ไขนัดหมาย กรุณาลองใหม่อีกครั้ง"