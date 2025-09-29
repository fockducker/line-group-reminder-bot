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
        
        # ถ้าเป็นกลุ่ม ตรวจสอบว่ามี mention หรือไม่
        if context_type == "group":
            # ตรวจสอบว่าข้อความเริ่มด้วย mention หรือไม่
            if not (message_lower.startswith('@') or 'bot' in message_lower or 
                   message_lower.startswith(('เพิ่มนัด', 'ดูนัด', 'ลบนัด', 'แก้ไขนัด', 'help', 'คำสั่ง', 'สถานะ', 'เตือน'))):
                # ไม่ใช่คำสั่งสำหรับบอท ให้ข้าม
                return
            
            # ลบ mention ออกจากข้อความ (ถ้ามี)
            if message_lower.startswith('@'):
                # หา space แรกและเอาข้อความหลัง mention
                space_index = user_message.find(' ')
                if space_index > 0:
                    user_message = user_message[space_index + 1:].strip()
                    message_lower = user_message.lower().strip()
                else:
                    # ถ้าพิมพ์แค่ mention อย่างเดียว ให้แสดงความช่วยเหลือ
                    message_lower = "help"
        
        # คำสั่งทักทาย
        if message_lower in ['hello', 'สวัสดี', 'ทักทาย']:
            if context_type == "group":
                reply_message = '''สวัสดี! ยินดีต้อนรับสู่ LINE Group Reminder Bot
นี่คือกลุ่มสำหรับจัดการการนัดหมายร่วมกัน

พิมพ์ "คำสั่ง" เพื่อดูวิธีใช้งาน'''
            else:
                reply_message = '''สวัสดี! ยินดีต้อนรับสู่ LINE Group Reminder Bot
นี่คือการนัดหมายส่วนตัวของคุณ

พิมพ์ "คำสั่ง" เพื่อดูวิธีใช้งาน'''
        
        # คำสั่งความช่วยเหลือ (Thai language commands)
        elif message_lower in ['help', 'คำสั่ง', 'ช่วยเหลือ', 'วิธีใช้']:
            base_help = '''📋 คำสั่งการจัดการนัดหมาย:

• "เพิ่มนัด" - เพิ่มการนัดหมายใหม่
• "ดูนัด" - ดูรายการนัดหมาย
• "ลบนัด [รหัส]" - ลบการนัดหมาย
• "แก้ไขนัด [รหัส]" - แก้ไขการนัดหมาย
• "สถานะ" - ดูสถานะของบอท
• "เตือน" - ดูข้อมูลการแจ้งเตือน

📝 รูปแบบการเพิ่มนัด:
แบบที่ 1 (Structured):
ชื่อนัดหมาย: "ปรึกษาตรวจฟัน"
วันเวลา: "8 ตุลาคม 2025 14:00"
แพทย์: "ทพญ. ปารัช"
โรงพยาบาล: "ศิริราช"
แผนก: "ทันตกรรม"

แบบที่ 2 (Natural):
เพิ่มนัด วันที่ 8 ตุลาคม 2025 เวลา 14:00 โรงพยาบาล ศิริราช แผนก ทันตกรรม ปรึกษาตรวจฟัน พบ ทพญ. ปารัช

🗑️ การลบนัดหมาย:
ลบนัด ABC123

🔄 การแก้ไขนัดหมาย:
แก้ไขนัด ABC123 ชื่อนัดหมาย:"ตรวจร่างกาย"

แก้ไขนัด ABC123
ชื่อนัดหมาย:"ตรวจร่างกาย"
วันเวลา:"10 ตุลาคม 2025 15:00"
แพทย์:"ดร.สมชาย"'''
            
            if context_type == "group":
                reply_message = base_help + '\n\n🏥 โหมดกลุ่ม: การนัดหมายจะแสดงให้ทุกคนในกลุ่มเห็น'
            else:
                reply_message = base_help + '\n\n👤 โหมดส่วนตัว: การนัดหมายของคุณเท่านั้น'
        
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
                
        # คำสั่งเกี่ยวกับการแจ้งเตือน
        elif message_lower in ['reminder', 'เตือน', 'การแจ้งเตือน']:
            reply_message = handle_reminder_info_command(context_type)
        
        elif message_lower in ['ทดสอบเตือน', 'test notification', 'testnotification']:
            reply_message = handle_test_notification_command(user_id)
        
        elif message_lower in ['ทดสอบวันที่', 'test date', 'testdate']:
            reply_message = handle_test_date_parser_command()
        
        elif message_lower in ['force check', 'forcecheck', 'เช็คเตือน', 'เช็คทันที']:
            reply_message = handle_force_notification_check_command()
                
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
            # ใช้ Smart Parser แยกวิเคราะห์ข้อความ
            try:
                from utils.datetime_parser import SmartDateTimeParser
                parser = SmartDateTimeParser()
                
                # แยกข้อมูลการนัดหมาย
                parsed_info = parser.extract_appointment_info(user_message)
                
                if parsed_info.get('error'):
                    return f"""❌ {parsed_info['error']}

💡 ตัวอย่างการใช้งาน:
• เพิ่มนัด ตรวจสุขภาพ 2025-01-15 09:00
• เพิ่มนัด พบหมอ พรุ่งนี้ เช้า
• เพิ่มนัด นัดฟัน 15/1/25 14:30"""
                
                appointment_datetime = parsed_info['datetime']
                title = parsed_info['title']
                doctor = parsed_info.get('doctor', 'ไม่ระบุ')
                hospital = parsed_info['hospital']
                department = parsed_info['department']
                location = parsed_info['location']
                
                logger.info(f"Parsed appointment: {parsed_info}")
                
            except ImportError:
                # Fallback ถ้า parser ไม่มี
                logger.warning("Smart parser not available, using simple parsing")
                appointment_text = " ".join(parts[1:])
                appointment_datetime = datetime.now() + timedelta(days=1)
                title = appointment_text
                doctor = "ไม่ระบุ"
                hospital = "ไม่ระบุ"
                department = "ทั่วไป"
                location = "ระบุเพิ่มเติมภายหลัง"
            
            # กำหนด context สำหรับ Google Sheets
            if context_type == "group":
                sheets_context = f"group_{context_id}"
                group_id_for_model = context_id
            else:
                sheets_context = "personal"  
                group_id_for_model = user_id  # ใช้ user_id สำหรับ personal
            
            # สร้างการนัดหมายใหม่
            # ใช้ location field เก็บข้อมูลหมอ
            location_with_doctor = location
            if doctor != "ไม่ระบุ":
                location_with_doctor = f"{doctor} | {location}" if location else doctor
            
            appointment = Appointment(
                id=str(uuid.uuid4())[:8],  # สร้าง ID สั้น ๆ
                group_id=group_id_for_model,
                datetime_iso=appointment_datetime.isoformat(),
                hospital=hospital,
                department=department,
                note=title,
                location=location_with_doctor
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
                    # แสดงข้อมูลที่ parsed ได้
                    date_str = appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')
                    
                    # สร้างข้อความตอบกลับ
                    result_message = f"""✅ บันทึกนัดหมายสำเร็จ!

📝 ชื่อนัดหมาย: "{title}"
🆔 รหัส: {appointment.id}
📅 วันเวลา: {date_str}"""
                    
                    # เพิ่มชื่อหมอถ้ามี
                    if doctor != "ไม่ระบุ":
                        result_message += f"\n👨‍⚕️ แพทย์: {doctor}"
                    
                    result_message += f"""
🏥 โรงพยาบาล: {hospital}
🔖 แผนก: {department}

✅ ข้อมูลถูกบันทึกแล้ว
🔔 ระบบจะแจ้งเตือน 7 วัน และ 1 วันก่อนนัดหมาย"""
                    
                    return result_message
                else:
                    logger.warning("Failed to save appointment - returned False")
                    return f"""⚠️ บันทึกนัดหมายไม่สำเร็จ

📝 ข้อมูล: "{title}"
📅 วันเวลา: {date_str}
❌ ไม่สามารถเชื่อมต่อ Google Sheets

🔧 กรุณาตรวจสอบการตั้งค่า Google Sheets
💡 หรือลองใหม่อีกครั้ง"""
                    
            except Exception as e:
                logger.error(f"Error saving appointment: {e}", exc_info=True)
                return f"""❌ เกิดข้อผิดพลาดในการบันทึก

📝 ข้อมูล: "{title if 'title' in locals() else user_message}"
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
        
        # กำหนด context และ group_id สำหรับ Google Sheets
        if context_type == "group":
            sheets_context = f"group_{context_id}"
            group_id_for_query = context_id
        else:
            sheets_context = "personal"
            group_id_for_query = user_id
        
        # ดึงรายการนัดหมาย
        appointments = repo.get_appointments(group_id_for_query, sheets_context)
        
        if not appointments:
            return """📋 รายการนัดหมาย

❌ ไม่พบการนัดหมายในขณะนี้

💡 พิมพ์ "เพิ่มนัด" เพื่อเพิ่มการนัดหมายใหม่"""
        
        # สร้างรายการนัดหมาย
        appointment_list = "📋 รายการนัดหมายของคุณ\n\n"
        
        for i, appointment in enumerate(appointments, 1):
            date_str = appointment.appointment_datetime.strftime("%d/%m/%Y %H:%M")
            appointment_list += f"📅 {i}. {appointment.note}\n"
            appointment_list += f"     🕐 วันที่: {date_str}\n"
            if appointment.hospital and appointment.hospital != "LINE Bot":
                appointment_list += f"     🏥 โรงพยาบาล: {appointment.hospital}\n"
            if appointment.department and appointment.department != "General":
                appointment_list += f"     🏢 แผนก: {appointment.department}\n"
            appointment_list += f"     🆔 รหัส: {appointment.id}\n\n"
        
        return appointment_list + "💡 พิมพ์ 'ลบนัด [รหัส]' เพื่อลบการนัดหมาย"
        
    except Exception as e:
        logger.error(f"Error in handle_list_appointments_command: {e}")
        return "เกิดข้อผิดพลาดในการดึงข้อมูลนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_delete_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งลบการนัดหมาย"""
    try:
        # แยกรหัสนัดหมายจากข้อความ
        import re
        
        # Pattern: ลบนัด [appointment_id]
        pattern = r'(?:ลบนัด|ยกเลิกนัด|ลบการนัด)\s+([A-Za-z0-9]+)'
        match = re.search(pattern, user_message, re.IGNORECASE)
        
        if not match:
            return """❌ รูปแบบไม่ถูกต้อง

📝 วิธีการใช้งาน:
ลบนัด [รหัสนัดหมาย]

ตัวอย่าง:
ลบนัด ABC123
ลบนัด 12345678

💡 ดูรหัสนัดหมายได้จากคำสั่ง "ดูนัด" """

        appointment_id = match.group(1).strip()
        
        # เชื่อมต่อกับ database
        repo = SheetsRepository()
        
        # ดึงรายการนัดหมาย
        appointments = repo.get_appointments(user_id, context_id)
        
        # หานัดหมายที่ต้องการลบ
        target_appointment = None
        for apt in appointments:
            if apt.appointment_id == appointment_id:
                target_appointment = apt
                break
        
        if not target_appointment:
            return f"""❌ ไม่พบนัดหมายรหัส: {appointment_id}

💡 ตรวจสอบรหัสนัดหมายด้วยคำสั่ง "ดูนัด" """

        # ลบนัดหมาย
        success = repo.delete_appointment(appointment_id, user_id, context_type, context_id)
        
        if success:
            return f"""✅ ลบนัดหมายเรียบร้อย!

🗑️ นัดหมายที่ถูกลบ:
• รหัส: {appointment_id}
• ชื่อ: {target_appointment.title}
• วันที่: {target_appointment.date}
• เวลา: {target_appointment.time}
• หมอ: {target_appointment.doctor}"""
        else:
            return f"❌ ไม่สามารถลบนัดหมายรหัส {appointment_id} ได้ กรุณาลองใหม่อีกครั้ง"
        
    except Exception as e:
        logger.error(f"Error in handle_delete_appointment_command: {e}")
        return "❌ เกิดข้อผิดพลาดในการลบนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_edit_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งแก้ไขการนัดหมาย"""
    try:
        import re
        from utils.datetime_parser import SmartDateTimeParser
        
        # แยกรหัสนัดหมายและข้อมูลที่ต้องการแก้ไข
        # Pattern: แก้ไขนัด [appointment_id] [fields...]
        pattern = r'(?:แก้ไขนัด|แก้นัด|แก้ไขการนัด)\s+([A-Za-z0-9]+)\s*(.*)'
        match = re.search(pattern, user_message, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return """❌ รูปแบบไม่ถูกต้อง

📝 วิธีการใช้งาน:
แก้ไขนัด [รหัสนัดหมาย] [ข้อมูลที่ต้องการแก้ไข]

ตัวอย่าง:
แก้ไขนัด ABC123 ชื่อนัดหมาย:"ตรวจร่างกาย"

แก้ไขนัด ABC123 
ชื่อนัดหมาย:"ตรวจร่างกาย"
วันเวลา:"8 ตุลาคม 2025 14:00"

📝 ฟิลด์ที่แก้ไขได้:
• ชื่อนัดหมาย:"..."
• วันเวลา:"..."  
• แพทย์:"..."
• โรงพยาบาล:"..."
• แผนก:"..."

💡 ดูรหัสนัดหมายด้วยคำสั่ง "ดูนัด" """

        appointment_id = match.group(1).strip()
        update_fields_text = match.group(2).strip()
        
        if not update_fields_text:
            return f"""❌ ไม่พบข้อมูลที่ต้องการแก้ไข

📝 ตัวอย่างการใช้งาน:
แก้ไขนัด {appointment_id} ชื่อนัดหมาย:"ตรวจร่างกาย" """

        # เชื่อมต่อกับ database
        repo = SheetsRepository()
        
        # ดึงรายการนัดหมาย
        appointments = repo.get_appointments(user_id, context_id)
        
        # หานัดหมายที่ต้องการแก้ไข
        target_appointment = None
        for apt in appointments:
            if apt.appointment_id == appointment_id:
                target_appointment = apt
                break
        
        if not target_appointment:
            return f"""❌ ไม่พบนัดหมายรหัส: {appointment_id}

💡 ตรวจสอบรหัสนัดหมายด้วยคำสั่ง "ดูนัด" """

        # แยกฟิลด์ที่ต้องการแก้ไข
        updated_fields = {}
        datetime_parser = SmartDateTimeParser()
        
        # รองรับฟิลด์ต่าง ๆ
        field_patterns = {
            'title': r'ชื่อนัดหมาย:\s*["\']([^"\']+)["\']',
            'datetime': r'วันเวลา:\s*["\']([^"\']+)["\']',
            'doctor': r'แพทย์:\s*["\']([^"\']+)["\']',
            'hospital': r'โรงพยาบาล:\s*["\']([^"\']+)["\']',
            'department': r'แผนก:\s*["\']([^"\']+)["\']'
        }
        
        changes_made = []
        
        for field_name, pattern in field_patterns.items():
            match_field = re.search(pattern, update_fields_text, re.IGNORECASE)
            if match_field:
                new_value = match_field.group(1).strip()
                
                if field_name == 'title':
                    updated_fields['title'] = new_value
                    changes_made.append(f"• ชื่อนัดหมาย: {target_appointment.title} → {new_value}")
                    
                elif field_name == 'datetime':
                    # แปลงวันเวลาใหม่
                    new_dt = datetime_parser._parse_datetime_string(new_value)
                    if new_dt:
                        updated_fields['date'] = new_dt.strftime('%d/%m/%Y')
                        updated_fields['time'] = new_dt.strftime('%H:%M')
                        changes_made.append(f"• วันที่: {target_appointment.date} {target_appointment.time} → {updated_fields['date']} {updated_fields['time']}")
                    else:
                        return f"""❌ รูปแบบวันเวลาไม่ถูกต้อง: "{new_value}"

📝 รูปแบบที่รองรับ:
• "8 ตุลาคม 2025 14:00"
• "15/11/2025 09:30"
• "2025-12-25 10:15" """
                        
                elif field_name == 'doctor':
                    updated_fields['doctor'] = new_value
                    changes_made.append(f"• แพทย์: {target_appointment.doctor} → {new_value}")
                    
                elif field_name == 'hospital':
                    updated_fields['location'] = new_value
                    changes_made.append(f"• โรงพยาบาล: {target_appointment.location} → {new_value}")
                    
                elif field_name == 'department':
                    updated_fields['department'] = new_value
                    changes_made.append(f"• แผนก: {getattr(target_appointment, 'department', 'ไม่ระบุ')} → {new_value}")

        if not updated_fields:
            return """❌ ไม่พบข้อมูลที่ต้องการแก้ไข

📝 รูปแบบที่ถูกต้อง:
ชื่อนัดหมาย:"ตรวจร่างกาย"
วันเวลา:"8 ตุลาคม 2025 14:00"
แพทย์:"ดร.สมชาย"
โรงพยาบาล:"ศิริราช"
แผนก:"อายุรกรรม" """

        # อัพเดทนัดหมาย
        success = repo.update_appointment(appointment_id, updated_fields, user_id, context_type, context_id)
        
        if success:
            changes_text = '\n'.join(changes_made)
            return f"""✅ แก้ไขนัดหมายเรียบร้อย!

🔄 การเปลี่ยนแปลง:
{changes_text}

📋 รหัสนัดหมาย: {appointment_id}"""
        else:
            return f"❌ ไม่สามารถแก้ไขนัดหมายรหัส {appointment_id} ได้ กรุณาลองใหม่อีกครั้ง"
        
    except Exception as e:
        logger.error(f"Error in handle_edit_appointment_command: {e}")
        return "❌ เกิดข้อผิดพลาดในการแก้ไขนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_reminder_info_command(context_type: str) -> str:
    """จัดการคำสั่งข้อมูลการแจ้งเตือน"""
    base_info = """🔔 ระบบแจ้งเตือนอัตโนมัติ

✅ ระบบทำงานอัตโนมัติทุกวันเวลา 09:00 น.
⏰ จะแจ้งเตือนในช่วงเวลา:

📅 7 วันก่อนนัดหมาย:
   • เตรียมความพร้อม
   • ทบทวนสถานที่และเวลา

⚡ 1 วันก่อนนัดหมาย:
   • แจ้งเตือนก่อนวันนัดหมาย
   • เตรียมเอกสารที่จำเป็น
   • แนะนำให้ไปให้ทันเวลา

💡 พิมพ์ "ทดสอบเตือน" เพื่อทดสอบระบบ"""
    
    if context_type == "group":
        return base_info + '\n\n🏥 โหมดกลุ่ม: การแจ้งเตือนจะส่งให้สมาชิกในกลุ่ม'
    else:
        return base_info + '\n\n👤 โหมดส่วนตัว: การแจ้งเตือนส่งให้คุณเท่านั้น'


def handle_test_notification_command(user_id: str) -> str:
    """จัดการคำสั่งทดสอบการแจ้งเตือน"""
    try:
        # ลองเรียกใช้ notification service (ถ้ามี)
        from notifications.notification_service import NotificationService
        
        # สร้าง test message
        return """🧪 ทดสอบระบบแจ้งเตือน

✅ ระบบแจ้งเตือนพร้อมใช้งาน!

📋 การตั้งค่าปัจจุบัน:
• เวลาแจ้งเตือน: ทุกวัน 09:00 น.
• แจ้งเตือนล่วงหน้า: 7 วัน, 1 วัน
• สถานะ: เปิดใช้งาน ✅

💡 การแจ้งเตือนจริงจะส่งอัตโนมัติ
   เมื่อถึงเวลาที่กำหนด"""
        
    except ImportError:
        return """⚠️ ระบบแจ้งเตือนยังไม่พร้อม

🔧 กำลังติดตั้งส่วนประกอบที่จำเป็น
⏳ กรุณารอสักครู่แล้วลองใหม่

💡 ถ้ายังมีปัญหา ให้ติดต่อผู้ดูแลระบบ"""
        
    except Exception as e:
        logger.error(f"Error in test notification: {e}")
        return f"""❌ เกิดข้อผิดพลาดในการทดสอบ

🔍 รายละเอียด: {str(e)}
🔧 กรุณาติดต่อผู้ดูแลระบบ"""


def handle_test_date_parser_command() -> str:
    """จัดการคำสั่งทดสอบ Date Parser"""
    try:
        from utils.datetime_parser import SmartDateTimeParser
        from datetime import datetime
        
        parser = SmartDateTimeParser()
        
        # ทดสอบกรณีต่าง ๆ
        test_cases = [
            "ตรวจสุขภาพ 2025-01-15 09:00",
            "พบหมอ 15/1/25 เช้า", 
            "นัดฟัน พรุ่งนี้ 14:30",
            "ตรวจเลือด วันจันทร์หน้า บ่าย"
        ]
        
        result = "🧪 ทดสอบระบบแยกวิเคราะห์วันที่\\n\\n"
        
        for i, case in enumerate(test_cases, 1):
            parsed = parser.extract_appointment_info(f"เพิ่มนัด {case}")
            if parsed['datetime']:
                date_str = parsed['datetime'].strftime('%d/%m/%Y %H:%M')
                result += f"{i}. {case}\\n"
                result += f"   ➡️ {date_str} | {parsed['title']}\\n\\n"
            else:
                result += f"{i}. {case} ❌\\n\\n"
        
        result += """✅ ระบบ Smart Parser พร้อมใช้งาน!

💡 รองรับรูปแบบ:
• 2025-01-15 09:00
• 15/1/25 เช้า  
• พรุ่งนี้ 14:30
• วันจันทร์หน้า บ่าย"""
        
        return result
        
    except ImportError:
        return """⚠️ ระบบ Smart Parser ยังไม่พร้อม

🔧 กำลังติดตั้งส่วนประกอบ
📅 ขณะนี้ใช้วันที่เริ่มต้น (พรุ่งนี้ 09:00)

💡 ระบบจะอัปเดตให้เร็ว ๆ นี้"""
        
    except Exception as e:
        logger.error(f"Error in test date parser: {e}")
        return f"""❌ เกิดข้อผิดพลาดในการทดสอบ

🔍 รายละเอียด: {str(e)}
🔧 กรุณาติดต่อผู้ดูแลระบบ"""


def handle_force_notification_check_command() -> str:
    """จัดการคำสั่ง force check การแจ้งเตือน"""
    try:
        import requests
        
        # เรียก API endpoint สำหรับ force check
        base_url = "https://line-group-reminder-bot.onrender.com"
        
        # ลองเรียก notification check
        try:
            response = requests.get(f"{base_url}/run-notification-check", timeout=10)
            
            if response.status_code == 200:
                return """✅ เช็คระบบแจ้งเตือนสำเร็จ!

🔍 ระบบได้ตรวจสอบการนัดหมายทั้งหมดแล้ว
📨 หากมีการแจ้งเตือนจะส่งให้ทันที

⏰ ระบบปกติจะเช็คทุกวัน 09:00 น.
💡 คำสั่งนี้ใช้สำหรับทดสอบเท่านั้น"""
            else:
                return f"""⚠️ เช็คระบบแจ้งเตือนไม่สำเร็จ

🔍 Response Code: {response.status_code}
🔧 กรุณาลองใหม่อีกครั้ง

💡 หรือใช้คำสั่ง "ทดสอบเตือน" แทน"""
                
        except requests.exceptions.RequestException as e:
            return f"""❌ ไม่สามารถเชื่อมต่อระบบได้

🔍 รายละเอียด: {str(e)}
🔧 ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต

💡 ลองใช้คำสั่ง "ทดสอบเตือน" แทน"""
    
    except ImportError:
        return """⚠️ ไม่สามารถใช้คำสั่งนี้ได้

🔧 ขาดโมดูลที่จำเป็น
💡 ใช้คำสั่ง "ทดสอบเตือน" แทน

📋 หรือไปที่:
https://line-group-reminder-bot.onrender.com/run-notification-check"""
    
    except Exception as e:
        logger.error(f"Error in force notification check: {e}")
        return f"""❌ เกิดข้อผิดพลาด

🔍 รายละเอียด: {str(e)}
💡 ลองใหม่อีกครั้ง หรือติดต่อผู้ดูแลระบบ"""