import os
from datetime import datetime
from flask import Flask, request, jsonify, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from dotenv import load_dotenv
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
        
        # เริ่มต้น Notification Service (แต่สั่งให้ start scheduler เฉพาะเมื่อ env var อนุญาต)
        if NOTIFICATION_ENABLED:
            try:
                notification_service = NotificationService(line_bot_api)
                # Only start the scheduler explicitly when START_NOTIFICATION_SCHEDULER env var is truthy
                start_flag = os.getenv('START_NOTIFICATION_SCHEDULER', 'false').lower()
                if start_flag in ('1', 'true', 'yes'):
                    notification_service.start_scheduler()
                    print("✅ Notification scheduler started successfully")
                else:
                    print("⚠️ Notification service initialized but scheduler not started in this process (set START_NOTIFICATION_SCHEDULER=1 to enable)")
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



@app.route('/migration')
def migration_page():
    """หน้าเว็บสำหรับรัน migration"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Sheets Migration</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .button { padding: 12px 24px; margin: 10px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: bold; text-decoration: none; display: inline-block; }
            .button:hover { transform: translateY(-1px); }
            .primary { background: #007bff; color: white; }
            .primary:hover { background: #0056b3; }
            .danger { background: #dc3545; color: white; }
            .danger:hover { background: #c82333; }
            .warning { background: #ffc107; color: black; }
            .warning:hover { background: #e0a800; }
            .success { background: #28a745; color: white; }
            .section { margin: 30px 0; padding: 20px; border-left: 4px solid #007bff; background: #f8f9fa; }
            .result { margin: 20px 0; padding: 15px; border-radius: 5px; white-space: pre-wrap; font-family: monospace; }
            .result.success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .result.error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            .loading { display: none; text-align: center; padding: 20px; }
            .warning-box { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Google Sheets Headers Migration</h1>
            <p>อัปเดท headers เก่าเป็นใหม่ใน Google Sheets สำหรับ LINE Bot</p>
            
            <div class="warning-box">
                <strong>⚠️ สำคัญ:</strong> กรุณา backup ข้อมูลใน Google Sheets ก่อนรัน migration!
            </div>
            
            <div class="section">
                <h3>📊 1. วิเคราะห์ Worksheets</h3>
                <p>ดูสถานะ worksheet ทั้งหมด - ไม่แก้ไขข้อมูลอะไร</p>
                <button class="button primary" onclick="runMigration('analyze')">📊 Analyze Worksheets</button>
            </div>
            
            <div class="section">
                <h3>🧪 2. ทดสอบ Migration (Dry Run)</h3>
                <p>ดูว่าจะเปลี่ยนอะไรบ้าง - ไม่แก้ไขข้อมูลจริง</p>
                <button class="button warning" onclick="runMigration('dry-run')">🧪 Dry Run Migration</button>
            </div>
            
            <div class="section">
                <h3>🚀 3. รัน Migration จริง</h3>
                <p><strong>⚠️ จะแก้ไข Google Sheets จริง! เขียนทับข้อมูลเก่า!</strong></p>
                <button class="button danger" onclick="confirmAndRun()">🚀 Execute Migration</button>
            </div>
            
            <div id="loading" class="loading">
                <h3>⏳ กำลังประมวลผล...</h3>
                <p>กรุณารอสักครู่ (อาจใช้เวลา 1-2 นาที)</p>
            </div>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            function confirmAndRun() {
                if (confirm('⚠️ แน่ใจหรือว่าต้องการแก้ไข Google Sheets?\\n\\n- จะเขียนทับข้อมูลเก่า\\n- hospital → location\\n- department → building_floor_dept\\n- doctor → contact_person\\n- เพิ่ม phone_number column\\n\\nกรุณายืนยันว่าได้ backup ข้อมูลแล้ว!')) {
                    runMigration('execute');
                }
            }
            
            async function runMigration(mode) {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    const response = await fetch('/migration/run', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ mode: mode })
                    });
                    
                    const data = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').innerHTML = data.output;
                    document.getElementById('result').className = 'result ' + (data.success ? 'success' : 'error');
                    
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').innerHTML = 'เกิดข้อผิดพลาด: ' + error.message;
                    document.getElementById('result').className = 'result error';
                }
            }
        </script>
    </body>
    </html>
    """
    return html


@app.route('/migration/run', methods=['POST'])
def run_migration():
    """รัน migration ตาม mode ที่เลือก"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'analyze')
        
        print(f"[MIGRATION] Running migration with mode: {mode}")
        
        # Import migrator
        from migrate_headers import HeaderMigrator
        
        # สร้าง migrator
        migrator = HeaderMigrator()
        
        if mode == 'analyze':
            analysis = migrator.analyze_worksheets()
            
            output = "📊 WORKSHEET ANALYSIS:\\n"
            output += "=" * 60 + "\\n"
            
            for name, info in analysis.items():
                status = info.get('status', 'unknown')
                needs_migration = info.get('needs_migration', False)
                data_rows = info.get('data_rows', 0)
                
                output += f"📄 {name}\\n"
                output += f"   Status: {status}\\n"
                output += f"   Data rows: {data_rows}\\n"
                output += f"   Needs migration: {'Yes' if needs_migration else 'No'}\\n"
                
                if 'headers' in info and info['headers']:
                    headers_str = ', '.join(info['headers'][:6])
                    if len(info['headers']) > 6:
                        headers_str += ", ..."
                    output += f"   Headers: [{headers_str}]\\n"
                output += "\\n"
            
            return jsonify({'success': True, 'output': output})
        
        elif mode == 'dry-run':
            results = migrator.migrate_all(dry_run=True)
            
            output = "🧪 DRY RUN RESULTS:\\n"
            output += "=" * 60 + "\\n"
            
            if not results:
                output += "✅ No worksheets need migration.\\n"
                output += "All worksheets are already in new format!\\n"
            else:
                output += f"Found {len(results)} worksheet(s) to migrate:\\n\\n"
                for worksheet, success in results.items():
                    status = "✅ Would succeed" if success else "❌ Would fail"
                    output += f"{status}: {worksheet}\\n"
                
                output += "\\n💡 This was a DRY RUN - no actual changes made.\\n"
                output += "Use 'Execute Migration' to apply changes.\\n"
            
            return jsonify({'success': True, 'output': output})
        
        elif mode == 'execute':
            print(f"[MIGRATION] Executing real migration...")
            results = migrator.migrate_all(dry_run=False)
            
            output = "🚀 MIGRATION RESULTS:\\n"
            output += "=" * 60 + "\\n"
            
            if not results:
                output += "✅ No worksheets needed migration.\\n"
                output += "All worksheets are already in new format!\\n"
                success = True
            else:
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                for worksheet, success in results.items():
                    status = "✅ Success" if success else "❌ Failed"
                    output += f"{status}: {worksheet}\\n"
                
                output += f"\\n📊 Summary: {success_count}/{total_count} worksheets migrated successfully\\n\\n"
                
                if success_count == total_count and total_count > 0:
                    output += "🎉 Migration completed successfully!\\n"
                    output += "\\n✅ Headers updated:\\n"
                    output += "   hospital → location\\n"
                    output += "   department → building_floor_dept\\n"
                    output += "   doctor → contact_person\\n"
                    output += "   + phone_number (empty)\\n"
                    success = True
                elif success_count > 0:
                    output += "⚠️ Migration partially successful.\\n"
                    output += "Check individual worksheet results above.\\n"
                    success = False
                else:
                    output += "❌ Migration failed.\\n"
                    output += "Check server logs for detailed error information.\\n"
                    success = False
            
            return jsonify({'success': success, 'output': output})
        
        else:
            return jsonify({'success': False, 'output': f'❌ Invalid mode: {mode}'})
    
    except Exception as e:
        error_msg = str(e)
        print(f"[MIGRATION] Error: {error_msg}")
        return jsonify({
            'success': False, 
            'output': f'❌ เกิดข้อผิดพลาด:\\n{error_msg}\\n\\nกรุณาตรวจสอบ:\\n- Environment variables ครบถ้วน\\n- เชื่อมต่อ Google Sheets ได้\\n- Service account มีสิทธิ์แก้ไข Sheets'
        })


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