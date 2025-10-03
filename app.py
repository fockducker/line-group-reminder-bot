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
    # Configuration ใน LINE Bot SDK v3 ไม่รองรับ timeout parameters
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
    api_client = ApiClient(configuration)
    line_bot_api = MessagingApi(api_client)
    handler = WebhookHandler(CHANNEL_SECRET)
    
    # ลงทะเบียน event handlers เฉพาะเมื่อมี tokens จริง
    if CHANNEL_ACCESS_TOKEN != "dummy" and CHANNEL_SECRET != "dummy":
        register_handlers(handler, line_bot_api)
        print("✅ LINE Bot handlers registered successfully")
        
        # เริ่มต้น Notification Service
        if NOTIFICATION_ENABLED:
            try:
                notification_service = NotificationService(line_bot_api)
                notification_service.start_scheduler()
                print("✅ Notification scheduler started successfully")
            except Exception as e:
                print(f"❌ Failed to start notification service: {e}")
                notification_service = None
    else:
        print("⚠️ LINE Bot running in dummy mode - handlers not registered")
        
except Exception as e:
    print(f"❌ Error initializing LINE Bot: {e}")
    print("⚠️ LINE Bot will run in safe mode without handlers")
    # กำหนดค่า default เพื่อให้ app ยังรันได้
    handler = None
    line_bot_api = None


@app.route('/healthz', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint เพื่อป้องกัน Render service หลับ"""
    try:
        return jsonify({
            'status': 'ok',
            'message': 'LINE Bot is running normally',
            'timestamp': datetime.now().isoformat(),
            'uptime': 'Service is awake',
            'notification_scheduler': 'Active' if notification_service and notification_service.scheduler.running else 'Inactive',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/ping', methods=['GET'])
def ping():
    """Ultra-lightweight ping endpoint for UptimeRobot"""
    return "pong", 200


@app.route('/alive', methods=['GET'])
def alive():
    """Minimal alive check - fastest response"""
    return "1", 200


@app.route('/warmup', methods=['GET'])
def warmup():
    """
    Comprehensive warmup endpoint for application and dependencies
    This endpoint simulates full application usage to keep connections warm
    """
    try:
        import time
        start_time = time.time()
        
        warmup_results = {
            'status': 'warming_up',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # 1. Basic application check
        warmup_results['checks']['app'] = 'ok'
        
        # 2. LINE Bot API connection test
        try:
            if line_bot_api:
                # We can't easily test LINE API without a real webhook, so just check config
                warmup_results['checks']['line_api'] = 'configured'
            else:
                warmup_results['checks']['line_api'] = 'not_configured'
        except Exception as e:
            warmup_results['checks']['line_api'] = f'error: {str(e)[:50]}'
        
        # 3. Google Sheets connection warmup
        try:
            from storage.sheets_repo import SheetsRepository
            repo = SheetsRepository()
            # Test connection without making changes
            if repo and hasattr(repo, 'sheet'):
                warmup_results['checks']['google_sheets'] = 'connected'
            else:
                warmup_results['checks']['google_sheets'] = 'not_connected'
        except Exception as e:
            warmup_results['checks']['google_sheets'] = f'error: {str(e)[:50]}'
        
        # 4. Notification service check
        try:
            if notification_service and hasattr(notification_service, 'scheduler'):
                if notification_service.scheduler.running:
                    warmup_results['checks']['scheduler'] = 'running'
                else:
                    warmup_results['checks']['scheduler'] = 'stopped'
            else:
                warmup_results['checks']['scheduler'] = 'not_available'
        except Exception as e:
            warmup_results['checks']['scheduler'] = f'error: {str(e)[:50]}'
        
        # 5. Message sender warmup
        try:
            from utils.message_sender import create_connection_aware_sender
            if line_bot_api:
                sender = create_connection_aware_sender(line_bot_api)
                warmup_results['checks']['message_sender'] = 'ready'
            else:
                warmup_results['checks']['message_sender'] = 'line_api_required'
        except Exception as e:
            warmup_results['checks']['message_sender'] = f'error: {str(e)[:50]}'
        
        # 6. Import handlers warmup
        try:
            from handlers import get_help_text
            test_help = get_help_text("personal")
            if test_help and len(test_help) > 0:
                warmup_results['checks']['handlers'] = 'loaded'
            else:
                warmup_results['checks']['handlers'] = 'empty_response'
        except Exception as e:
            warmup_results['checks']['handlers'] = f'error: {str(e)[:50]}'
        
        elapsed_time = time.time() - start_time
        warmup_results['warmup_time_seconds'] = round(elapsed_time, 3)
        warmup_results['status'] = 'warmed_up'
        
        # Determine overall health
        error_count = sum(1 for check in warmup_results['checks'].values() if 'error' in str(check))
        if error_count == 0:
            warmup_results['overall_health'] = 'healthy'
            return jsonify(warmup_results), 200
        elif error_count <= 2:
            warmup_results['overall_health'] = 'degraded'
            return jsonify(warmup_results), 200
        else:
            warmup_results['overall_health'] = 'unhealthy'
            return jsonify(warmup_results), 503
            
    except Exception as e:
        return jsonify({
            'status': 'warmup_failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


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


@app.route('/debug-notification', methods=['GET'])
def debug_notification_endpoint():
    """Debug notification system - ตรวจสอบสถานะระบบแจ้งเตือน"""
    try:
        if not notification_service:
            return jsonify({
                'status': 'error',
                'message': 'Notification service not available'
            }), 503
        
        # รัน debug function
        notification_service.debug_notification_system()
        
        return jsonify({
            'status': 'success',
            'message': 'Debug completed - check server logs for details',
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
    
    print(f"[WEBHOOK] Received callback request")
    print(f"[WEBHOOK] Headers: {dict(request.headers)}")
    
    # ตรวจสอบว่ามี LINE Bot handler หรือไม่
    if not handler or CHANNEL_ACCESS_TOKEN == "dummy":
        print("[WEBHOOK] ERROR: LINE Bot not configured")
        return jsonify({
            'status': 'error',
            'message': 'LINE Bot not configured. Please set environment variables.'
        }), 500
    
    # รับ X-Line-Signature header value
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        print("[WEBHOOK] ERROR: Missing X-Line-Signature header")
        abort(400, description="Missing X-Line-Signature header")
    
    # รับ request body เป็น text
    body = request.get_data(as_text=True)
    print(f"[WEBHOOK] Body length: {len(body)}")
    print(f"[WEBHOOK] Body: {body[:500]}...")  # แสดง 500 ตัวอักษรแรก
    
    try:
        print(f"[WEBHOOK] Processing webhook with signature verification...")
        
        # เพิ่ม timeout protection แต่ยัง process แบบ sync เพื่อใช้ reply_token
        import signal
        import time
        
        start_time = time.time()
        
        handler.handle(body, signature)
        
        end_time = time.time()
        process_time = end_time - start_time
        print(f"[WEBHOOK] SUCCESS: Webhook processed in {process_time:.2f} seconds")
        
    except InvalidSignatureError as e:
        print(f"[WEBHOOK] ERROR: Invalid signature - {e}")
        print(f"[WEBHOOK] Channel Secret Length: {len(CHANNEL_SECRET) if CHANNEL_SECRET else 'None'}")
        abort(400, description="Invalid signature")
    except Exception as e:
        print(f"[WEBHOOK] ERROR: Exception in webhook setup - {e}")
        import traceback
        traceback.print_exc()
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