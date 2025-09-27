"""
Event handlers module for LINE Group Reminder Bot
จัดการ event handlers สำหรับข้อความต่าง ๆ ที่ได้รับจาก LINE
"""

import logging
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

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
        logger.info(f"Received message: {user_message}")
        
        # ตัวอย่างการตอบกลับข้อความ
        if user_message.lower() == 'hello':
            reply_message = 'สวัสดี! ยินดีต้อนรับสู่ LINE Group Reminder Bot'
        elif user_message.lower() == 'help':
            reply_message = '''ความช่วยเหลือ:
- พิมพ์ "hello" เพื่อทักทาย
- พิมพ์ "help" เพื่อดูความช่วยเหลือ
- พิมพ์ "reminder" เพื่อดูข้อมูลการแจ้งเตือน
- พิมพ์ "status" เพื่อดูสถานะของบอท'''
        elif user_message.lower() == 'reminder':
            reply_message = '''การแจ้งเตือน:
ระบบการแจ้งเตือนอัตโนมัติจะพัฒนาในอนาคต
ขณะนี้บอทพร้อมรับข้อความและตอบกลับแล้ว'''
        elif user_message.lower() == 'status':
            reply_message = '''สถานะของบอท:
✅ เชื่อมต่อ LINE API สำเร็จ
✅ รับข้อความได้ปกติ
✅ ส่งข้อความตอบกลับได้ปกติ
🔄 ระบบ Scheduler พร้อมใช้งาน'''
        else:
            reply_message = f'คุณพิมพ์: "{user_message}"\n\nพิมพ์ "help" เพื่อดูคำสั่งที่ใช้ได้'
        
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