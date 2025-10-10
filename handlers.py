"""
Event handlers module for LINE Group Reminder Bot
จัดการ event handlers สำหรับข้อความต่าง ๆ ที่ได้รับจาก LINE
"""

import logging
import uuid
import time
from datetime import datetime, timedelta
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from storage.sheets_repo import SheetsRepository
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from storage.models import Appointment
from utils.message_sender import create_connection_aware_sender, MessageQueue

# Conditional import สำหรับ SheetsRepository
try:
    from storage.sheets_repo import SheetsRepository
    SHEETS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SheetsRepository not available: {e}")
    SHEETS_AVAILABLE = False
    
    class DummySheetsRepository:
        def __init__(self):
            pass
        def add_appointment(self, appointment):
            return False
        def get_appointments(self, group_id, context):
            return []
        def delete_appointment(self, appointment_id, context):
            return False
        def update_appointment(self, appointment_id, context, fields):
            return False
    
    SheetsRepository = DummySheetsRepository

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
        
        # ถ้าเป็นกลุ่ม ตรวจสอบว่าเป็นคำสั่งบอทหรือไม่
        if context_type == "group":
            # ตอบเฉพาะคำสั่งที่เกี่ยวข้องกับการจัดการนัดหมาย
            if not message_lower.startswith(('เพิ่มนัด', 'ดูนัด', 'ลบนัด', 'แก้ไขนัด', 'แก้นัด', 'ยกเลิกนัด', 'ลบการนัด', 'นัดใหม่', 'เพิ่มการนัด', 'แก้ไขการนัด',
                                              'ดูนัดย้อนหลัง', 'นัดย้อนหลัง', 'ประวัตินัด', 'ย้อนหลัง', 'ดูย้อนหลัง',
                                              'hello', 'สวัสดี', 'ทักทาย', 'help', 'คำสั่ง', 'สถานะ', 'เตือน', 'ทดสอบ')):
                # ไม่ใช่คำสั่งสำหรับบอท ให้ข้าม
                return
            
            # ลบ mention ออกจากข้อความ (ถ้ามี) เพื่อให้ประมวลผลต่อได้
            if message_lower.startswith('@'):
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
            base_help = '''📋 คำสั่งการจัดการนัดหมาย (รองรับภาษาไทยแบบธรรมชาติ):

• "เพิ่มนัด" - เพิ่มการนัดหมายใหม่
• "ดูนัด" - ดูรายการนัดหมายที่กำลังจะมาถึง
• "ดูนัดย้อนหลัง" - ดูประวัตินัดหมาย
• "ลบนัด [รหัส]" - ลบการนัดหมาย
• "แก้ไขนัด [รหัส]" - แก้ไขการนัดหมาย

📝 ตัวอย่างเพิ่มนัด (Natural Language):
• เพิ่มนัด ไปหาหมอ ศุกร์หน้า 9:30 ที่ โรงพยาบาลจุฬา แผนกหัวใจ กับหมอเอ
• เพิ่มนัด ประชุมทีม 24 ตุลา 15:00 at CentralWorld
• เพิ่มนัด กินข้าวกับที่บ้าน วันอาทิตย์ เย็น

📌 เคล็ดลับ:
• เดือนแบบย่อได้: ตุลา พฤศจิกา ธันวา ฯลฯ
• ปี พ.ศ. หรือ ย่อ 26 → 2026 ก็ได้
• เวลาแบบคำพูดได้: บ่ายสาม, สามทุ่มครึ่ง, เช้า

🗑️ ลบนัดหมาย:
ลบนัด ABC123

🔄 แก้ไขนัดหมาย:
แก้ไขนัด ABC123 นัดหมาย:"ตรวจร่างกาย"

หรือส่งหลายแถว:
แก้ไขนัด ABC123
นัดหมาย:"ตรวจสุขภาพ"
วันเวลา:"10 ตุลาคม 2025 15:00"
บุคคล/ผู้ติดต่อ:"ดร.สมชาย"'''
            
            if context_type == "group":
                reply_message = base_help + '\n\n🏥 โหมดกลุ่ม: การนัดหมายจะแสดงให้ทุกคนในกลุ่มเห็น'
            else:
                reply_message = base_help + '\n\n👤 โหมดส่วนตัว: การนัดหมายของคุณเท่านั้น'
        
        # คำสั่งเพิ่มการนัดหมาย (รองรับแบบยืดหยุ่น)
        elif message_lower.startswith(('เพิ่มนัด', 'นัดใหม่', 'เพิ่มการนัด')):
            reply_message = handle_add_appointment_command(user_message, user_id, context_type, context_id)
        
        # คำสั่งดูการนัดหมาย
        elif message_lower in ['ดูนัด', 'รายการนัด', 'นัดหมาย', 'ดูการนัด']:
            reply_message = handle_list_appointments_command(user_id, context_type, context_id, show_past=False)
            
        elif message_lower in ['ดูนัดย้อนหลัง', 'นัดย้อนหลัง', 'ประวัตินัด', 'ดูประวัตินัด']:
            reply_message = handle_historical_appointments_menu(user_id, context_type, context_id)
            
        elif message_lower.startswith(('ย้อนหลัง', 'ดูย้อนหลัง')):
            reply_message = handle_historical_appointments_command(user_message, user_id, context_type, context_id)
        
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
        
        # ส่งข้อความตอบกลับด้วย robust sender
        sender = create_connection_aware_sender(line_bot_api)
        success, error = sender.send_reply_with_timeout(event.reply_token, reply_message)
        
        if not success:
            logger.error(f"Failed to send reply after retries: {error}")
            # Send fallback message
            sender.send_fallback_message(event.reply_token)
    
    logger.info("LINE event handlers registered successfully")


def get_help_text(context_type: str = "personal") -> str:
    """Get help text for testing and warmup purposes"""
    base_help = '''📋 คำสั่งการจัดการนัดหมาย (Enhanced Parser):

• "เพิ่มนัด" - เพิ่มการนัดหมายใหม่
• "ดูนัด" - ดูรายการนัดหมาย
• "ลบนัด [รหัส]" - ลบการนัดหมาย
• "แก้ไขนัด [รหัส]" - แก้ไขการนัดหมาย
• "สถานะ" - ดูสถานะของบอท
• "เตือน" - ดูข้อมูลการแจ้งเตือน

📝 ตัวอย่างเพิ่มนัด (Natural):
• เพิ่มนัด พบหมอ พฤหัส หน้า 10:00 ที่ รพ.จุฬา แผนกหัวใจ
• เพิ่มนัด ประชุม 24 ตุลาคม บ่ายสาม at CentralWorld
• เพิ่มนัด ไปเที่ยว 1 ม.ค. 26 เช้า

        📌 ใช้เดือนไทยเต็ม/ย่อ/ภาษาพูดได้ เช่น ตุลา พฤศจิกา ธันวา
📌 ปี พ.ศ. แปลงเป็น ค.ศ. อัตโนมัติ (เช่น 2569 → 2026)'''
    
    if context_type == "group":
        return base_help + '\n\n🏥 โหมดกลุ่ม: การนัดหมายจะแสดงให้ทุกคนในกลุ่มเห็น'
    else:
        return base_help + '\n\n👤 โหมดส่วนตัว: การนัดหมายของคุณเท่านั้น'


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
            return """การเพิ่มนัดหมายใหม่ (Enhanced Smart Parser)

พิมพ์ธรรมชาติได้เลย เช่น:
• เพิ่มนัด ไปหาหมอ ศุกร์หน้า 9:30 ที่ โรงพยาบาลจุฬา แผนกหัวใจ กับหมอเอ
• เพิ่มนัด ประชุมทีม 24 ตุลา 15:00 at CentralWorld
• เพิ่มนัด กินข้าวกับที่บ้าน วันอาทิตย์ เย็น

เคล็ดลับ:
• เดือนไทยย่อได้: ตุลา พฤศจิกา ธันวา ฯลฯ
• ปี พ.ศ. หรือ 2 หลัก 26 → 2026 ได้
• เวลาแบบคำพูด: บ่ายสาม, สามทุ่มครึ่ง, เช้า
"""
        
        # ถ้ามีข้อมูลเพิ่มเติม ให้ทำการประมวลผลและบันทึกจริง
        else:
            # ใช้ Smart Parser แยกวิเคราะห์ข้อความ
            try:
                from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser
                parser = EnhancedSmartDateTimeParser()

                info = parser.extract_appointment_info(user_message)
                appointment_datetime = info.get('datetime')
                if not appointment_datetime:
                    return """❌ ยังจับวันเวลาไม่ชัดเจน

ลองพิมพ์ให้ระบุวันเวลาให้มากขึ้น เช่น:
• เพิ่มนัด พบหมอ พฤหัสนี้ 10:00 ที่ รพ.จุฬา
• เพิ่มนัด ประชุม 24 ตุลา 15:00 at CentralWorld
• เพิ่มนัด ไปเที่ยว 1 ม.ค. 26 เช้า"""

                title = info.get('appointment_title', 'นัดหมาย')
                location = info.get('location', '')
                building_floor_dept = info.get('building_dept', '')
                contact_person = info.get('contact_person', '')
                phone_number = info.get('phone_number', '')

                logger.info(f"Parsed appointment (enhanced): {info}")
                
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
                group_id_for_model = user_id
            
            # สร้างการนัดหมายใหม่
            appointment = Appointment(
                id=str(uuid.uuid4())[:8],  # สร้าง ID สั้น ๆ
                group_id=group_id_for_model,
                datetime_iso=appointment_datetime.isoformat(),
                location=location,
                building_floor_dept=building_floor_dept or "",
                contact_person=contact_person or "",
                phone_number=phone_number or "",
                note=title
            )
            
            logger.info(f"Created appointment: {appointment.to_dict()}")
            
            # บันทึกลง Google Sheets
            try:
                logger.info(f"Attempting to save appointment with context: {sheets_context}")
                logger.info(f"Appointment data: {appointment.to_dict()}")
                
                repo = SheetsRepository()
                logger.info(f"SheetsRepository created successfully. Connected: {repo.gc is not None}")
                logger.info(f"Spreadsheet available: {repo.spreadsheet is not None}")
                
                # แสดงข้อมูลที่ parsed ได้ (ก่อนการบันทึก)
                date_str = appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')
                
                success = repo.add_appointment(appointment)
                logger.info(f"Add appointment result: {success}")
                
                if success:
                    # ตรวจสอบว่าเป็นนัดหมายในอดีตหรือไม่
                    import pytz
                    bangkok_tz = pytz.timezone('Asia/Bangkok')
                    now = datetime.now(bangkok_tz)
                    is_past_appointment = appointment.appointment_datetime < now
                    
                    # สร้างข้อความตอบกลับ
                    if is_past_appointment:
                        result_message = f"""⚠️ คำเตือน: นัดหมายในอดีต!

📝 ชื่อนัดหมาย: "{title}"
🆔 รหัส: {appointment.id}
📅 วันเวลา: {date_str} (อดีต)"""
                    else:
                        result_message = f"""✅ บันทึกนัดหมายสำเร็จ!

📝 ชื่อนัดหมาย: "{title}"
🆔 รหัส: {appointment.id}
📅 วันเวลา: {date_str}"""
                    
                    # เพิ่มผู้ติดต่อ/สถานที่ถ้ามี
                    if contact_person:
                        result_message += f"\n👤 บุคคล/ผู้ติดต่อ: {contact_person}"
                    result_message += f"""
📍 สถานที่: {location or 'ไม่ระบุ'}
🏢 อาคาร/แผนก/ชั้น: {building_floor_dept or 'ไม่ระบุ'}

✅ ข้อมูลถูกบันทึกแล้ว"""

                    # เพิ่มข้อความเตือนและคำแนะนำตามประเภทนัดหมาย
                    if is_past_appointment:
                        result_message += f"""
📋 นัดหมายนี้จะปรากฏใน "ดูนัดย้อนหลัง" เท่านั้น
💡 หากต้องการดูใช้คำสั่ง "ดูนัดย้อนหลัง"
⚠️ ระบบแจ้งเตือนจะไม่ทำงานกับนัดหมายในอดีต"""
                    else:
                        result_message += f"""
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


def handle_list_appointments_command(user_id: str, context_type: str, context_id: str, show_past: bool = True) -> str:
    """จัดการคำสั่งดูรายการนัดหมาย
    
    Args:
        show_past (bool): True = แสดงทั้งอนาคตและอดีต, False = แสดงเฉพาะอนาคต
    """
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
        
        # เรียงลำดับตามวันที่ (ใกล้ที่สุดก่อน - อนาคตก่อน แล้วตามด้วยอดีต)
        from datetime import datetime
        import pytz
        
        # ใช้ Bangkok timezone เหมือนกับ appointment datetime
        bangkok_tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(bangkok_tz)
        
        # แยกนัดหมายออกเป็นอนาคตและอดีต
        future_appointments = [apt for apt in appointments if apt.appointment_datetime >= now]
        past_appointments = [apt for apt in appointments if apt.appointment_datetime < now]
        
        # เรียงอนาคต: ใกล้ที่สุดก่อน (ascending)
        future_appointments.sort(key=lambda apt: apt.appointment_datetime)
        
        # เรียงอดีต: ล่าสุดก่อน (descending) 
        past_appointments.sort(key=lambda apt: apt.appointment_datetime, reverse=True)
        
        # รวมกันตาม show_past parameter
        if show_past:
            # แสดงทั้งอนาคตและอดีต (เดิม)
            appointments = future_appointments + past_appointments
            list_title = "📋 รายการนัดหมายของคุณ"
        else:
            # แสดงเฉพาะอนาคต (ใหม่)
            appointments = future_appointments
            list_title = "📋 นัดหมายที่กำลังจะมาถึง"
        
        # จำกัดการแสดงผลเพื่อป้องกันข้อความยาวเกินไป
        MAX_APPOINTMENTS = 10  # แสดงแค่ 10 รายการแรก
        total_appointments = len(appointments)
        
        if total_appointments > MAX_APPOINTMENTS:
            appointments = appointments[:MAX_APPOINTMENTS]
            
        # สร้างรายการนัดหมาย
        appointment_list = f"{list_title} ({total_appointments} รายการ)\n\n"
        
        for i, appointment in enumerate(appointments, 1):
            date_str = appointment.appointment_datetime.strftime("%d/%m/%Y %H:%M")
            
            # เพิ่ม indicator สำหรับนัดหมายอนาคต/อดีต
            if appointment.appointment_datetime >= now:
                status_icon = "🔴"  # นัดหมายใกล้ถึง
            else:
                status_icon = "⚪"  # นัดหมายที่ผ่านมาแล้ว
            
            appointment_list += f"📅 {i}. {status_icon} {appointment.note}\n"
            appointment_list += f"     🕐 {date_str}\n"
            if appointment.location and appointment.location != "LINE Bot":
                appointment_list += f"     📍 {appointment.location}\n"
            if appointment.building_floor_dept and appointment.building_floor_dept != "General":
                appointment_list += f"     🏢 {appointment.building_floor_dept}\n"
            if getattr(appointment, 'contact_person', None) and appointment.contact_person:
                appointment_list += f"     👤 {appointment.contact_person}\n"
            if getattr(appointment, 'phone_number', None) and appointment.phone_number:
                appointment_list += f"     📞 {appointment.phone_number}\n"
            appointment_list += f"     🆔 {appointment.id}\n\n"
        
        # เพิ่มข้อความถ้ามีการนัดหมายมากกว่าที่แสดง
        if show_past:
            footer = """💡 คำสั่งที่เป็นประโยชน์:
• 'ลบนัด [รหัส]' เพื่อลบการนัดหมาย
• 'ดูนัด' เพื่อดูเฉพาะนัดหมายที่กำลังจะมาถึง

🔴 = นัดหมายใกล้ถึง
⚪ = นัดหมายที่ผ่านแล้ว"""
        else:
            footer = """💡 คำสั่งที่เป็นประโยชน์:
• 'ลบนัด [รหัส]' เพื่อลบการนัดหมาย  
• 'ดูนัดย้อนหลัง' เพื่อดูประวัตินัดหมายที่ผ่านมา

🔴 = นัดหมายใกล้ถึง"""
        
        if total_appointments > MAX_APPOINTMENTS:
            footer = f"""⚠️ แสดง {MAX_APPOINTMENTS} จาก {total_appointments} รายการ
สำหรับรายการทั้งหมดใช้เว็บหรือ Google Sheets

""" + footer
        
        return appointment_list + footer
        
    except Exception as e:
        logger.error(f"Error in handle_list_appointments_command: {e}")
        return "เกิดข้อผิดพลาดในการดึงข้อมูลนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_historical_appointments_menu(user_id: str, context_type: str, context_id: str) -> str:
    """แสดงเมนูเลือกระยะเวลาย้อนหลัง"""
    
    menu = f"""📚 ดูประวัตินัดหมายย้อนหลัง

⏰ เลือกระยะเวลาที่ต้องการดู:

🔢 **ระยะเวลาย้อนหลัง:**
• พิมพ์ "ย้อนหลัง 1 เดือน" หรือ "ดูย้อนหลัง 1 เดือน"
• พิมพ์ "ย้อนหลัง 2 เดือน" หรือ "ดูย้อนหลัง 2 เดือน"
• พิมพ์ "ย้อนหลัง 3 เดือน" หรือ "ดูย้อนหลัง 3 เดือน"
• พิมพ์ "ย้อนหลัง 6 เดือน" หรือ "ดูย้อนหลัง 6 เดือน"
• พิมพ์ "ย้อนหลัง 1 ปี" หรือ "ดูย้อนหลัง 1 ปี"

📅 **เดือนเฉพาะ:**
• พิมพ์ "ย้อนหลัง ตุลาคม 2025" หรือ "ดูย้อนหลัง ตุลาคม 2025"
• พิมพ์ "ย้อนหลัง กันยายน 2025" หรือ "ดูย้อนหลัง กันยายน 2025"
• พิมพ์ "ย้อนหลัง สิงหาคม 2025" เป็นต้น

💡 ตัวอย่าง: "ย้อนหลัง 2 เดือน" หรือ "ย้อนหลัง มีนาคม 2025" """
    
    return menu


def handle_historical_appointments_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งดูนัดหมายย้อนหลัง"""
    import re
    from datetime import datetime, timedelta
    import pytz
    
    try:
        # ใช้ Bangkok timezone
        bangkok_tz = pytz.timezone('Asia/Bangkok')
        now = datetime.now(bangkok_tz)
        
        message_lower = user_message.lower()
        
        # Pattern สำหรับระยะเวลาย้อนหลัง
        months_pattern = r'(?:ย้อนหลัง|ดูย้อนหลัง)\s*(\d+)\s*(?:เดือน|month)'
        year_pattern = r'(?:ย้อนหลัง|ดูย้อนหลัง)\s*(\d+)\s*(?:ปี|year)'
        
        # Pattern สำหรับเดือนเฉพาะ (ใช้ word boundary และ unicode range ที่เฉพาะเจาะจง)
        specific_month_pattern = r'(?:ย้อนหลัง|ดูย้อนหลัง)\s+(มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม)\s+(\d{4})'
        
        start_date = None
        end_date = None
        period_description = ""
        
        # ตรวจสอบ pattern เดือนย้อนหลัง
        months_match = re.search(months_pattern, message_lower)
        if months_match:
            months = int(months_match.group(1))
            if months > 12:
                return "❌ สามารถดูย้อนหลังได้สูงสุด 12 เดือน"
            
            start_date = now - timedelta(days=months * 30)  # ประมาณ 30 วันต่อเดือน
            end_date = now
            period_description = f"{months} เดือนที่ผ่านมา"
            
        # ตรวจสอบ pattern ปีย้อนหลัง  
        elif re.search(year_pattern, message_lower):
            year_match = re.search(year_pattern, message_lower)
            years = int(year_match.group(1))
            if years > 2:
                return "❌ สามารถดูย้อนหลังได้สูงสุด 2 ปี"
                
            start_date = now - timedelta(days=years * 365)
            end_date = now
            period_description = f"{years} ปีที่ผ่านมา"
            
        # ตรวจสอบ pattern เดือนเฉพาะ
        elif re.search(specific_month_pattern, message_lower):
            month_match = re.search(specific_month_pattern, message_lower)
            month_thai = month_match.group(1)
            year = int(month_match.group(2))
            
            # แปลงเดือนไทยเป็นตัวเลข
            thai_months = {
                'มกราคม': 1, 'กุมภาพันธ์': 2, 'มีนาคม': 3, 'เมษายน': 4,
                'พฤษภาคม': 5, 'มิถุนายน': 6, 'กรกฎาคม': 7, 'สิงหาคม': 8,
                'กันยายน': 9, 'ตุลาคม': 10, 'พฤศจิกายน': 11, 'ธันวาคม': 12
            }
            
            month_num = thai_months.get(month_thai)
            if not month_num:
                return f"❌ ไม่พบเดือน '{month_thai}' กรุณาใช้ชื่อเดือนภาษาไทยที่ถูกต้อง"
            
            # สร้างช่วงเวลาของเดือนนั้น
            start_date = datetime(year, month_num, 1, 0, 0, 0, tzinfo=bangkok_tz)
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=bangkok_tz)
            else:
                end_date = datetime(year, month_num + 1, 1, 0, 0, 0, tzinfo=bangkok_tz)
                
            period_description = f"{month_thai} {year}"
            
        else:
            return """❌ รูปแบบไม่ถูกต้อง

💡 ตัวอย่างที่ถูกต้อง:
• "ย้อนหลัง 2 เดือน"
• "ดูย้อนหลัง 6 เดือน" 
• "ย้อนหลัง 1 ปี"
• "ย้อนหลัง ตุลาคม 2025"
• "ดูย้อนหลัง กันยายน 2025" """
        
        # ดึงข้อมูลนัดหมาย
        repo = SheetsRepository()
        
        if context_type == "group":
            sheets_context = f"group_{context_id}"
            group_id_for_query = context_id
        else:
            sheets_context = "personal"
            group_id_for_query = user_id
        
        appointments = repo.get_appointments(group_id_for_query, sheets_context)
        
        if not appointments:
            return f"""📚 ประวัตินัดหมาย - {period_description}

❌ ไม่พบการนัดหมายในช่วงเวลาที่ระบุ

💡 พิมพ์ "ดูนัดย้อนหลัง" เพื่อเลือกช่วงเวลาอื่น"""
        
        # กรองนัดหมายในช่วงเวลาที่กำหนด
        filtered_appointments = []
        for apt in appointments:
            if start_date <= apt.appointment_datetime < end_date:
                filtered_appointments.append(apt)
        
        if not filtered_appointments:
            return f"""📚 ประวัตินัดหมาย - {period_description}

❌ ไม่พบการนัดหมายในช่วงเวลาที่ระบุ

💡 พิมพ์ "ดูนัดย้อนหลัง" เพื่อเลือกช่วงเวลาอื่น"""
        
        # เรียงลำดับจากใหม่ไปเก่า
        filtered_appointments.sort(key=lambda apt: apt.appointment_datetime, reverse=True)
        
        # จำกัดการแสดงผล
        MAX_HISTORICAL = 20
        total_found = len(filtered_appointments)
        
        if total_found > MAX_HISTORICAL:
            filtered_appointments = filtered_appointments[:MAX_HISTORICAL]
        
        # สร้างรายการ
        appointment_list = f"""📚 ประวัตินัดหมาย - {period_description}
พบ {total_found} รายการ

"""
        
        for i, appointment in enumerate(filtered_appointments, 1):
            date_str = appointment.appointment_datetime.strftime("%d/%m/%Y %H:%M")
            
            appointment_list += f"📅 {i}. ⚪ {appointment.note}\n"
            appointment_list += f"     🕐 {date_str}\n"
            if appointment.location and appointment.location != "LINE Bot":
                appointment_list += f"     📍 {appointment.location}\n"
            if appointment.building_floor_dept and appointment.building_floor_dept != "General":
                appointment_list += f"     🏢 {appointment.building_floor_dept}\n"
            if getattr(appointment, 'contact_person', None) and appointment.contact_person:
                appointment_list += f"     👤 {appointment.contact_person}\n"
            if getattr(appointment, 'phone_number', None) and appointment.phone_number:
                appointment_list += f"     📞 {appointment.phone_number}\n"
            appointment_list += f"     🆔 {appointment.id}\n\n"
        
        # Footer
        footer = "⚪ = นัดหมายที่ผ่านแล้ว\n💡 พิมพ์ \"ดูนัดย้อนหลัง\" เพื่อเลือกช่วงเวลาอื่น"
        
        if total_found > MAX_HISTORICAL:
            footer = f"""⚠️ แสดง {MAX_HISTORICAL} จาก {total_found} รายการ

""" + footer
        
        return appointment_list + footer
        
    except Exception as e:
        logger.error(f"Error in handle_historical_appointments_command: {e}")
        return "เกิดข้อผิดพลาดในการดึงข้อมูลประวัตินัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_delete_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งลบการนัดหมาย - ใช้ robust message sending"""
    try:
        from linebot.v3.messaging import MessagingApi, PushMessageRequest, TextMessage, Configuration, ApiClient
        import os
        import re
        
        # แยกรหัสนัดหมายจากข้อความ
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
        
        # เริ่ม background deletion process ด้วย robust messaging
        try:
            channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
            if channel_access_token:
                configuration = Configuration(access_token=channel_access_token)
                api_client = ApiClient(configuration)
                line_bot_api = MessagingApi(api_client)
                
                # สร้าง robust sender
                sender = create_connection_aware_sender(line_bot_api)
                
                target_id = context_id if context_type == "group" else user_id
                
                # ข้อความยืนยัน
                confirmation_message = f"⏳ กำลังลบนัดหมาย {appointment_id}...\nรอสักครู่นะคะ"
                
                # ส่งข้อความยืนยันทันที
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=target_id,
                        messages=[TextMessage(text=confirmation_message)]
                    )
                )
                logger.info(f"Sent deletion confirmation for appointment {appointment_id}")
                
                # ดำเนินการลบและส่งผลลัพธ์
                def process_deletion():
                    try:
                        # เชื่อมต่อกับ database
                        repo = SheetsRepository()
                        
                        # กำหนด context
                        if context_type == "group":
                            sheets_context = f"group_{context_id}"
                            group_id_for_query = context_id
                        else:
                            sheets_context = "personal"
                            group_id_for_query = user_id
                        
                        # ดึงรายการนัดหมาย
                        appointments = repo.get_appointments(group_id_for_query, sheets_context)
                        
                        logger.info(f"Delete attempt - Found {len(appointments)} appointments for group_id: {group_id_for_query}, context: {sheets_context}")
                        for apt in appointments:
                            logger.info(f"Available appointment ID: {apt.id}")
                        
                        # หานัดหมายที่ต้องการลบ
                        target_appointment = None
                        for apt in appointments:
                            if apt.id == appointment_id:
                                target_appointment = apt
                                break
                        
                        if not target_appointment:
                            final_message = f"""❌ ไม่พบนัดหมายรหัส: {appointment_id}

💡 ตรวจสอบรหัสนัดหมายด้วยคำสั่ง "ดูนัด" """
                        else:
                            # ลบนัดหมาย
                            success = repo.delete_appointment(appointment_id, sheets_context)
                            
                            if success:
                                final_message = f"""✅ ลบนัดหมายเรียบร้อย!

🗑️ นัดหมายที่ถูกลบ:
• รหัส: {appointment_id}
• ชื่อ: {target_appointment.title}
• วันที่: {target_appointment.date}
• เวลา: {target_appointment.time}
• บุคคล/ผู้ติดต่อ: {target_appointment.contact_person}"""
                            else:
                                final_message = f"❌ ไม่สามารถลบนัดหมายรหัส {appointment_id} ได้ กรุณาลองใหม่อีกครั้ง"
                        
                        # ส่งผลลัพธ์ด้วย robust sender
                        line_bot_api.push_message(
                            PushMessageRequest(
                                to=target_id,
                                messages=[TextMessage(text=final_message)]
                            )
                        )
                        logger.info(f"Sent final deletion result for appointment {appointment_id}")
                        
                    except Exception as e:
                        logger.error(f"Error in deletion process: {e}")
                        # ส่งข้อความ error
                        error_message = f"❌ เกิดข้อผิดพลาดในการลบนัดหมาย {appointment_id}"
                        try:
                            line_bot_api.push_message(
                                PushMessageRequest(
                                    to=target_id,
                                    messages=[TextMessage(text=error_message)]
                                )
                            )
                        except:
                            pass
                
                # Run deletion in background thread
                import threading
                thread = threading.Thread(target=process_deletion)
                thread.daemon = True
                thread.start()
                
                return "🔄 กำลังดำเนินการลบนัดหมาย..."
                
        except Exception as e:
            logger.error(f"Failed to setup deletion process: {e}")
            return f"❌ ไม่สามารถเริ่มกระบวนการลบนัดหมาย {appointment_id} ได้"
        
    except Exception as e:
        logger.error(f"Error in handle_delete_appointment_command: {e}")
        return "❌ เกิดข้อผิดพลาดในการลบนัดหมาย กรุณาลองใหม่อีกครั้ง"


def handle_edit_appointment_command(user_message: str, user_id: str, context_type: str, context_id: str) -> str:
    """จัดการคำสั่งแก้ไขการนัดหมาย"""
    try:
        import re
        from datetime import datetime
        from utils.datetime_parser import SmartDateTimeParser
        
        logger.info(f"[EDIT] Processing edit command: {user_message}")
        logger.info(f"[EDIT] User: {user_id}, Context: {context_type}, Context ID: {context_id}")
        
        # แยกรหัสนัดหมายและข้อมูลที่ต้องการแก้ไข
        # Pattern: แก้ไขนัด [appointment_id] [fields...]
        pattern = r'(?:แก้ไขนัด|แก้นัด|แก้ไขการนัด)\s+([A-Za-z0-9]+)\s*(.*)'
        match = re.search(pattern, user_message, re.IGNORECASE | re.DOTALL)
        
        logger.info(f"[EDIT] Regex match result: {match.groups() if match else 'No match'}")
        
        if not match:
            return """❌ รูปแบบไม่ถูกต้อง

📝 วิธีการใช้งาน:
แก้ไขนัด [รหัสนัดหมาย] [ข้อมูลที่ต้องการแก้ไข]

ตัวอย่าง:
แก้ไขนัด ABC123 นัดหมาย:"ตรวจร่างกาย"

แก้ไขนัด ABC123 
นัดหมาย:"ตรวจสุขภาพ"
วันที่:"8 ตุลาคม 2025"
เวลา:"14:00"
สถานที่:"โรงพยาบาลศิริราช"
อาคาร/แผนก/ชั้น:"อาคาร 1 ชั้น 3"
บุคคล/ผู้ติดต่อ:"นพ.สมชาย"
เบอร์โทร:"02-419-7000"

📝 ฟิลด์ที่แก้ไขได้:
• นัดหมาย:"..."
• วันที่:"..." และ เวลา:"..."
• สถานที่:"..."
• อาคาร/แผนก/ชั้น:"..."
• บุคคล/ผู้ติดต่อ:"..."
• เบอร์โทร:"..."

💡 ดูรหัสนัดหมายด้วยคำสั่ง "ดูนัด" """

        appointment_id = match.group(1).strip()
        update_fields_text = match.group(2).strip()
        
        if not update_fields_text:
            return f"""❌ ไม่พบข้อมูลที่ต้องการแก้ไข

📝 ตัวอย่างการใช้งาน:
แก้ไขนัด {appointment_id} นัดหมาย:"ตรวจร่างกาย"

หรือแก้ไขหลายฟิลด์:
แก้ไขนัด {appointment_id}
นัดหมาย:"ตรวจสุขภาพ"
วันที่:"8 ตุลาคม 2025"
เวลา:"14:00"
เบอร์โทร:"02-419-7000" """

        # เชื่อมต่อกับ database
        repo = SheetsRepository()
        
        # กำหนด context และ group_id สำหรับ Google Sheets
        if context_type == "group":
            sheets_context = f"group_{context_id}"
            group_id_for_query = context_id
        else:
            sheets_context = "personal"
            group_id_for_query = user_id
            
        logger.info(f"[EDIT] Using context: {sheets_context}, group_id: {group_id_for_query}")
        
        # ดึงรายการนัดหมาย
        appointments = repo.get_appointments(group_id_for_query, sheets_context)
        
        # Debug logging
        logger.info(f"[EDIT] Found {len(appointments)} appointments for group_id: {group_id_for_query}, context: {sheets_context}")
        for apt in appointments:
            logger.info(f"Available appointment ID: {apt.id}")
        
        # หานัดหมายที่ต้องการแก้ไข
        target_appointment = None
        for apt in appointments:
            if apt.id == appointment_id:
                target_appointment = apt
                break
        
        if not target_appointment:
            return f"""❌ ไม่พบนัดหมายรหัส: {appointment_id}

💡 ตรวจสอบรหัสนัดหมายด้วยคำสั่ง "ดูนัด" """

        # แยกฟิลด์ที่ต้องการแก้ไข
        updated_fields = {}
        datetime_parser = SmartDateTimeParser()
        
        # รองรับฟิลด์ต่าง ๆ (รองรับทั้งแบบมี quotes และไม่มี)
        field_patterns = {
            'title': r'(?:นัดหมาย|ชื่อนัดหมาย):\s*["\']([^"\']+)["\']',
            'date': r'วันที่:\s*["\']([^"\']+)["\']',
            'time': r'เวลา:\s*["\']([^"\']+)["\']',
            'datetime': r'วันเวลา:\s*["\']([^"\']+)["\']',
            'contact_person': r'(?:บุคคล/ผู้ติดต่อ|แพทย์|บุคคล|ผู้ติดต่อ):\s*["\']([^"\']+)["\']',
            'location': r'(?:สถานที่|โรงพยาบาล):\s*["\']([^"\']+)["\']',
            'building_floor_dept': r'(?:อาคาร/แผนก/ชั้น|แผนก|อาคาร|ชั้น):\s*["\']([^"\']+)["\']',
            'phone_number': r'(?:เบอร์โทร|โทรศัพท์):\s*["\']([^"\']+)["\']'
        }
        
        changes_made = []
        date_value = None
        time_value = None
        
        for field_name, pattern in field_patterns.items():
            match_field = re.search(pattern, update_fields_text, re.IGNORECASE)
            if match_field:
                new_value = match_field.group(1).strip()
                
                if field_name == 'title':
                    updated_fields['note'] = new_value
                    changes_made.append(f"• ชื่อนัดหมาย: {getattr(target_appointment, 'note', 'ไม่ระบุ')} → {new_value}")
                    
                elif field_name == 'date':
                    date_value = new_value
                    
                elif field_name == 'time':
                    time_value = new_value
                    
                elif field_name == 'datetime':
                    # แปลงวันเวลาใหม่
                    logger.info(f"[EDIT] Parsing datetime: '{new_value}'")
                    new_dt = datetime_parser._parse_datetime_string(new_value)
                    logger.info(f"[EDIT] Parsed result: {new_dt}")
                    if new_dt:
                        updated_fields['datetime_iso'] = new_dt.isoformat()
                        old_dt = datetime.fromisoformat(target_appointment.datetime_iso.replace('Z', ''))
                        logger.info(f"[EDIT] Old datetime: {old_dt}, New datetime: {new_dt}")
                        changes_made.append(f"• วันที่: {old_dt.strftime('%d/%m/%Y %H:%M')} → {new_dt.strftime('%d/%m/%Y %H:%M')}")
                    else:
                        return f"""❌ รูปแบบวันเวลาไม่ถูกต้อง: "{new_value}"

📝 รูปแบบที่รองรับ:
• "8 ตุลาคม 2025 14:00"
• "15/11/2025 09:30"
• "2025-12-25 10:15" """
                        
                elif field_name == 'contact_person':
                    updated_fields['contact_person'] = new_value
                    changes_made.append(f"• บุคคล/ผู้ติดต่อ: {getattr(target_appointment, 'contact_person', 'ไม่ระบุ')} → {new_value}")
                    
                elif field_name == 'location':
                    updated_fields['location'] = new_value
                    changes_made.append(f"• สถานที่: {getattr(target_appointment, 'location', 'ไม่ระบุ')} → {new_value}")
                    
                elif field_name == 'building_floor_dept':
                    updated_fields['building_floor_dept'] = new_value
                    changes_made.append(f"• อาคาร/แผนก/ชั้น: {getattr(target_appointment, 'building_floor_dept', 'ไม่ระบุ')} → {new_value}")
                    
                elif field_name == 'phone_number':
                    updated_fields['phone_number'] = new_value
                    changes_made.append(f"• เบอร์โทร: {getattr(target_appointment, 'phone_number', 'ไม่ระบุ')} → {new_value}")
                    
        # จัดการ date + time แยกกัน
        if date_value or time_value:
            # รวม date + time
            if date_value and time_value:
                datetime_string = f"{date_value} {time_value}"
            elif date_value:
                # ใช้เวลาเดิม
                old_dt = datetime.fromisoformat(target_appointment.datetime_iso.replace('Z', ''))
                datetime_string = f"{date_value} {old_dt.strftime('%H:%M')}"
            elif time_value:
                # ใช้วันที่เดิม
                old_dt = datetime.fromisoformat(target_appointment.datetime_iso.replace('Z', ''))
                datetime_string = f"{old_dt.strftime('%d %B %Y')} {time_value}"
            
            logger.info(f"[EDIT] Parsing combined datetime: '{datetime_string}'")
            new_dt = datetime_parser._parse_datetime_string(datetime_string)
            
            if new_dt:
                updated_fields['datetime_iso'] = new_dt.isoformat()
                old_dt = datetime.fromisoformat(target_appointment.datetime_iso.replace('Z', ''))
                changes_made.append(f"• วันที่: {old_dt.strftime('%d/%m/%Y %H:%M')} → {new_dt.strftime('%d/%m/%Y %H:%M')}")
            else:
                return f"""❌ รูปแบบวันที่/เวลาไม่ถูกต้อง: "{datetime_string}"

📝 รูปแบบที่รองรับ:
• วันที่: "8 ตุลาคม 2025" เวลา: "14:00"
• วันที่: "15/11/2025" เวลา: "09:30" """
                    
        if not updated_fields:
            return """❌ ไม่พบข้อมูลที่ต้องการแก้ไข

📝 รูปแบบที่ถูกต้อง:
นัดหมาย:"ตรวจร่างกาย"
วันที่:"8 ตุลาคม 2025"
เวลา:"14:00"
สถานที่:"โรงพยาบาลศิริราช"
อาคาร/แผนก/ชั้น:"อาคาร 1 ชั้น 3"
บุคคล/ผู้ติดต่อ:"นพ.สมชาย"
เบอร์โทร:"02-419-7000"

💡 สามารถแก้ไขหลายฟิลด์พร้อมกัน """

        # อัพเดทนัดหมาย
        success = repo.update_appointment(appointment_id, sheets_context, updated_fields)
        
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