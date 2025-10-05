"""
Web endpoint สำหรับรัน migration ผ่าน browser
เพิ่มใน main.py หรือสร้างไฟล์แยก
"""

from flask import Flask, request, jsonify, render_template_string
from migrate_headers import HeaderMigrator
import logging
import json

# เพิ่ม routes ใน main.py
@app.route('/migration')
def migration_page():
    """หน้าเว็บสำหรับรัน migration"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Sheets Migration</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .button { padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .button:hover { background: #0056b3; }
            .danger { background: #dc3545; }
            .danger:hover { background: #c82333; }
            .warning { background: #ffc107; color: black; }
            .success { background: #28a745; }
            .result { margin: 20px 0; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
            .loading { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Google Sheets Headers Migration</h1>
            
            <div>
                <h3>📊 1. วิเคราะห์ Worksheets</h3>
                <p>ดูสถานะ worksheet ทั้งหมด (ไม่แก้ไขอะไร)</p>
                <button class="button" onclick="runMigration('analyze')">Analyze Worksheets</button>
            </div>
            
            <div>
                <h3>🧪 2. ทดสอบ Migration (Dry Run)</h3>
                <p>ดูว่าจะเปลี่ยนอะไรบ้าง (ไม่แก้ไขจริง)</p>
                <button class="button warning" onclick="runMigration('dry-run')">Dry Run Migration</button>
            </div>
            
            <div>
                <h3>🚀 3. รัน Migration จริง</h3>
                <p><strong>⚠️ จะแก้ไข Google Sheets จริง!</strong></p>
                <button class="button danger" onclick="runMigration('execute')" 
                        onclick="return confirm('⚠️ แน่ใจหรือว่าต้องการแก้ไข Google Sheets? กรุณา backup ข้อมูลก่อน!')">
                    Execute Migration
                </button>
            </div>
            
            <div id="loading" class="loading">
                <h3>⏳ กำลังประมวลผล...</h3>
                <p>กรุณารอสักครู่</p>
            </div>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            async function runMigration(mode) {
                if (mode === 'execute') {
                    if (!confirm('⚠️ แน่ใจหรือว่าต้องการแก้ไข Google Sheets? จะเขียนทับข้อมูลเก่า!')) {
                        return;
                    }
                }
                
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
                    document.getElementById('result').className = 'result ' + (data.success ? 'success' : 'danger');
                    
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').innerHTML = 'Error: ' + error.message;
                    document.getElementById('result').className = 'result danger';
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
        
        logger.info(f"Running migration with mode: {mode}")
        
        # สร้าง migrator
        migrator = HeaderMigrator()
        
        if mode == 'analyze':
            analysis = migrator.analyze_worksheets()
            
            output = "📊 WORKSHEET ANALYSIS:\\n"
            output += "=" * 50 + "\\n"
            
            for name, info in analysis.items():
                status = info.get('status', 'unknown')
                needs_migration = info.get('needs_migration', False)
                data_rows = info.get('data_rows', 0)
                
                output += f"📄 {name}\\n"
                output += f"   Status: {status}\\n"
                output += f"   Data rows: {data_rows}\\n"
                output += f"   Needs migration: {'Yes' if needs_migration else 'No'}\\n"
                
                if 'headers' in info and info['headers']:
                    output += f"   Headers: {info['headers']}\\n"
                output += "\\n"
            
            return jsonify({'success': True, 'output': output})
        
        elif mode == 'dry-run':
            results = migrator.migrate_all(dry_run=True)
            
            output = "🧪 DRY RUN RESULTS:\\n"
            output += "=" * 50 + "\\n"
            
            if not results:
                output += "No worksheets need migration.\\n"
            else:
                for worksheet, success in results.items():
                    status = "✅ Would succeed" if success else "❌ Would fail"
                    output += f"{status}: {worksheet}\\n"
            
            return jsonify({'success': True, 'output': output})
        
        elif mode == 'execute':
            results = migrator.migrate_all(dry_run=False)
            
            output = "🚀 MIGRATION RESULTS:\\n"
            output += "=" * 50 + "\\n"
            
            if not results:
                output += "No worksheets needed migration.\\n"
                success = True
            else:
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                for worksheet, success in results.items():
                    status = "✅ Success" if success else "❌ Failed"
                    output += f"{status}: {worksheet}\\n"
                
                output += f"\\nSummary: {success_count}/{total_count} worksheets migrated successfully\\n"
                
                if success_count == total_count and total_count > 0:
                    output += "🎉 Migration completed successfully!\\n"
                    success = True
                elif success_count > 0:
                    output += "⚠️ Migration partially successful.\\n"
                    success = False
                else:
                    output += "❌ Migration failed.\\n"
                    success = False
            
            return jsonify({'success': success, 'output': output})
        
        else:
            return jsonify({'success': False, 'output': f'Invalid mode: {mode}'})
    
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return jsonify({'success': False, 'output': f'Error: {str(e)}'})