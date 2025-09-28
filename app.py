import os
from datetime import datetime
from flask import Flask, request, jsonify, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from dotenv import load_dotenv
from scheduler import run_scheduled_push
from handlers import register_handlers

# เพิ่ม Notification Service
try:
    from notifications.notification_service import NotificationService
    NOTIFICATION_ENABLED = True
except ImportError as e:
    print(f"Warning: Notification service not available: {e}")
    NOTIFICATION_ENABLED = False

# โหลด environment variables จากไฟล์ .env
load_dotenv()

app = Flask(__name__)

# รับค่า configuration จาก environment variables
# รองรับทั้งชื่อเดิมและชื่อใหม่สำหรับ Render
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN') or os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET') or os.getenv('CHANNEL_SECRET')
# Render จะกำหนด PORT อัตโนมัติ หรือใช้ค่าเริ่มต้น
PORT = int(os.getenv('PORT', 10000))

# ตรวจสอบว่ามี required environment variables
if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("Warning: LINE_CHANNEL_ACCESS_TOKEN และ LINE_CHANNEL_SECRET ไม่ได้ตั้งค่า")
    print("LINE webhook จะไม่ทำงาน แต่ app จะรันต่อเพื่อให้ตั้งค่าได้")
    # ไม่ exit เพื่อให้สามารถเข้า health check ได้
    CHANNEL_ACCESS_TOKEN = "dummy"
    CHANNEL_SECRET = "dummy"

# สร้าง Configuration และ MessagingApi สำหรับ v3
notification_service = None
try:
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
    api_client = ApiClient(configuration)
    line_bot_api = MessagingApi(api_client)
    handler = WebhookHandler(CHANNEL_SECRET)
    
    # ลงทะเบียน event handlers เฉพาะเมื่อมี tokens จริง
    if CHANNEL_ACCESS_TOKEN != "dummy" and CHANNEL_SECRET != "dummy":
        register_handlers(handler, line_bot_api)
        print("LINE Bot handlers registered successfully")
        
        # เริ่มต้น Notification Service
        if NOTIFICATION_ENABLED:
            try:
                notification_service = NotificationService(line_bot_api)
                notification_service.start_scheduler()
                print("✅ Notification scheduler started successfully")
            except Exception as e:
                print(f"❌ Failed to start notification service: {e}")
    else:
        print("Skipping LINE Bot handler registration due to missing credentials")
except Exception as e:
    print(f"Error initializing LINE Bot: {e}")
    handler = None
    line_bot_api = None


@app.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint สำหรับตรวจสอบสถานะของ application"""
    return jsonify({
        'status': 'ok',
        'message': 'LINE Bot is running'
    }), 200


@app.route('/run-scheduler', methods=['GET'])
def run_scheduler_endpoint():
    """Scheduler endpoint สำหรับเรียกใช้งานจาก cron job"""
    try:
        now = datetime.now()
        run_scheduled_push(now)
        return jsonify({
            'status': 'success',
            'message': 'scheduler ok',
            'timestamp': now.isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/test-notification', methods=['POST', 'GET'])
def test_notification_endpoint():
    """ทดสอบระบบแจ้งเตือน"""
    try:
        if not notification_service:
            return jsonify({
                'status': 'error',
                'message': 'Notification service not available'
            }), 503
        
        # รับ user_id จาก request (หรือใช้ test user)
        if request.method == 'POST':
            data = request.get_json()
            user_id = data.get('user_id') if data else None
        else:
            user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'user_id is required'
            }), 400
        
        # ส่งการแจ้งเตือนทดสอบ
        success = notification_service.send_test_notification(user_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Test notification sent to {user_id}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send test notification'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/run-notification-check', methods=['GET'])
def run_notification_check_endpoint():
    """รัน notification check ทันทีสำหรับทดสอบ"""
    try:
        if not notification_service:
            return jsonify({
                'status': 'error',
                'message': 'Notification service not available'
            }), 503
        
        # รัน notification check ทันที
        notification_service.check_and_send_notifications()
        
        return jsonify({
            'status': 'success',
            'message': 'Notification check completed',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/callback', methods=['POST'])
def callback():
    """Webhook endpoint สำหรับรับข้อความจาก LINE"""
    
    # ตรวจสอบว่ามี LINE Bot handler หรือไม่
    if not handler or CHANNEL_ACCESS_TOKEN == "dummy":
        return jsonify({
            'status': 'error',
            'message': 'LINE Bot not configured. Please set environment variables.'
        }), 500
    
    # รับ X-Line-Signature header value
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        abort(400, description="Missing X-Line-Signature header")
    
    # รับ request body เป็น text
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel secret.")
        abort(400, description="Invalid signature")
    except Exception as e:
        print(f"Error handling webhook: {e}")
        abort(500, description="Internal server error")
    
    return 'OK', 200



@app.errorhandler(404)
def not_found(error):
    """จัดการ 404 error"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint was not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """จัดการ 500 error"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server'
    }), 500


if __name__ == '__main__':
    print(f"Starting LINE Bot server on port {PORT}")
    print("Make sure to set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET environment variables")
    app.run(host='0.0.0.0', port=PORT, debug=True)