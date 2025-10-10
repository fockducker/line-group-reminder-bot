#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct GUI launcher - no dependencies
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from datetime import datetime
import uuid
import re

def test_parser():
    """Test parser without importing"""
    
    # Simulate enhanced parser result for demo
    test_input = "เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง"
    
    # Mock result based on our parser logic
    result = {
        'original_text': test_input,
        'appointment_title': 'กินข้าวเที่ยว',
        'date': '07/10/2025',
        'time': '15.00',
        'location': '',
        'building_dept': '',
        'contact_person': 'ที่รัก',
        'phone_number': '',
        'confidence': 0.7
    }
    
    return result

def format_result(result):
    """Format result for display"""
    formatted = "🔍 PARSE RESULTS\n"
    formatted += "=" * 50 + "\n\n"
    
    formatted += f"📝 Original Text: {result.get('original_text', '')}\n\n"
    
    formatted += "📊 EXTRACTED DATA:\n"
    formatted += "-" * 30 + "\n"
    
    fields = [
        ('นัดหมาย', result.get('appointment_title', '')),
        ('วันที่', result.get('date', '')),
        ('เวลา', result.get('time', '')),
        ('สถานที่', result.get('location', '')),
        ('อาคาร/แผนก/ชั้น', result.get('building_dept', '')),
        ('บุคคล/ผู้ติดต่อ', result.get('contact_person', '')),
        ('เบอร์โทร', result.get('phone_number', ''))
    ]
    
    for field_name, field_value in fields:
        if field_value:
            formatted += f"{field_name}: \"{field_value}\"\n"
    
    formatted += f"\nConfidence Score: {result.get('confidence', 0):.2f}\n"
    
    return formatted

class SimpleParserTester:
    """Simple parser tester app"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Enhanced Smart Parser Tester (Demo)")
        self.root.geometry("800x600")
        
        # In-memory appointment store (volatile)
        # Each record: {
        #   id, created_at, original_text, appointment_title, date, time,
        #   location, contact_person, phone_number, confidence
        # }
        self.appointments = []
        self.max_records = 500  # simple cap
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 Enhanced Smart Parser Tester", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="📝 Input Text", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="พิมพ์ข้อความที่ต้องการทดสอบ:").pack(anchor=tk.W)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, width=70, height=4)
        self.input_text.pack(fill=tk.X, pady=(5, 10))
        
        # Pre-fill with example
        self.input_text.insert(1.0, "เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง")
        
        # Parse button
        self.parse_button = ttk.Button(input_frame, text="🔍 Parse Text", 
                                      command=self.parse_text)
        self.parse_button.pack()
        
        # Split lower area into left (results) and right (history)
        lower_frame = ttk.Frame(main_frame)
        lower_frame.pack(fill=tk.BOTH, expand=True)

        # Results section (left)
        results_frame = ttk.LabelFrame(lower_frame, text="📊 Parse Results", padding="8")
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        self.results_text = scrolledtext.ScrolledText(results_frame, width=50, height=18)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        btn_row = ttk.Frame(results_frame)
        btn_row.pack(fill=tk.X, pady=(6,0))
        self.export_button = ttk.Button(btn_row, text="💾 Export JSON", command=self.export_json)
        self.export_button.pack(side=tk.LEFT)
        self.clear_input_button = ttk.Button(btn_row, text="🧹 Clear Input", command=lambda: self.input_text.delete(1.0, tk.END))
        self.clear_input_button.pack(side=tk.LEFT, padx=4)

        # History section (right)
        history_frame = ttk.LabelFrame(lower_frame, text="🗂️ History (ไม่บันทึกถาวร)", padding="8")
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        cols = ("idx","title","date","time","location","building","contact","phone","confidence")
        self.history_tree = ttk.Treeview(history_frame, columns=cols, show='headings', height=15)
        headings = {
            'idx': '#',
            'title': 'นัดหมาย',
            'date': 'วันที่',
            'time': 'เวลา',
            'location': 'สถานที่',
            'building': 'อาคาร/ชั้น',
            'contact': 'ผู้ติดต่อ',
            'phone': 'เบอร์',
            'confidence': 'Conf.'
        }
        col_widths = {
            'idx': 40, 'title': 140, 'date': 80, 'time': 70, 'location': 120,
            'building': 110, 'contact': 100, 'phone': 90, 'confidence': 60
        }
        for c in cols:
            self.history_tree.heading(c, text=headings[c])
            self.history_tree.column(c, width=col_widths.get(c, 90), anchor=tk.W, stretch=(c in ['title','location','building']))
        # Add vertical scrollbar
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        hist_btns = ttk.Frame(history_frame)
        hist_btns.pack(fill=tk.X, pady=(6,0))
        ttk.Button(hist_btns, text="❌ ลบรายการ", command=self.delete_selected).pack(side=tk.LEFT)
        ttk.Button(hist_btns, text="🧺 ล้างทั้งหมด", command=self.clear_all).pack(side=tk.LEFT, padx=4)
        ttk.Button(hist_btns, text="🔄 Refresh", command=self.refresh_history).pack(side=tk.LEFT)
        
        # Status
        self.status_var = tk.StringVar(value="พร้อมใช้งาน - กด Parse Text เพื่อทดสอบ")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=(10, 0))
    
    def parse_text(self):
        """Parse input text"""
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("Warning", "กรุณาใส่ข้อความที่ต้องการ parse")
            return
        
        try:
            self.status_var.set("กำลัง parse ข้อความ...")
            self.root.update()
            
            # Detect if command (edit/delete) first
            if self.handle_command(input_text):
                return

            parse_outcome = self.run_parser(input_text)
            self.current_result = parse_outcome
            formatted_result = format_result(parse_outcome)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, formatted_result)

            # Store into in-memory list
            self.store_result(parse_outcome)
            self.refresh_history()
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, error_msg)
            self.status_var.set("Parse failed")
    
    def export_json(self):
        """Export result as JSON"""
        if not hasattr(self, 'current_result'):
            messagebox.showwarning("Warning", "ไม่มีผลลัพธ์ให้ export")
            return
        
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Parse Results as JSON"
            )
            
            if filename:
                # Remove empty fields
                export_data = {k: v for k, v in self.current_result.items() 
                             if v and v != ''}
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Success", f"Results exported to {filename}")
                self.status_var.set(f"Exported to JSON")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    # ================== In-memory storage helpers ==================
    def run_parser(self, text: str) -> dict:
        """Run underlying parser (real or fallback) and normalize output."""
        try:
            # Prefer absolute package import
            from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser
            parser = EnhancedSmartDateTimeParser()
            result = parser.extract_appointment_info(text)
            clean_result = {
                'original_text': result.get('original_text', text),
                'appointment_title': result.get('appointment_title', ''),
                'date': result.get('date', ''),
                'time': result.get('time', ''),
                'location': result.get('location', ''),
                'building_dept': result.get('building_dept', ''),
                'contact_person': result.get('contact_person', ''),
                'phone_number': result.get('phone_number', ''),
                'confidence': result.get('confidence', 0)
            }
            self.status_var.set(f"✅ Parse สำเร็จ - Confidence: {clean_result.get('confidence', 0):.2f}")
            return clean_result
        except Exception:
            # Fallback to demo if parser import/execution fails
            demo = test_parser()
            self.status_var.set("⚠️ Demo mode (parser import failed)")
            return demo

    def store_result(self, result: dict):
        record = {
            'id': str(uuid.uuid4())[:8],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **result
        }
        self.appointments.append(record)
        # Trim if exceed max
        if len(self.appointments) > self.max_records:
            self.appointments = self.appointments[-self.max_records:]

    def refresh_history(self):
        # Clear tree
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for idx, appt in enumerate(self.appointments, start=1):
            self.history_tree.insert('', 'end', iid=appt['id'], values=(
                idx,
                appt.get('appointment_title','') or '',
                appt.get('date','') or '',
                appt.get('time','') or '',
                appt.get('location','') or '',
                appt.get('building_dept','') or '',
                appt.get('contact_person','') or '',
                appt.get('phone_number','') or '',
                f"{appt.get('confidence',0):.2f}"
            ))

    def delete_selected(self):
        sel = self.history_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "เลือกนัดที่จะลบก่อน")
            return
        sel_ids = set(sel)
        self.appointments = [a for a in self.appointments if a['id'] not in sel_ids]
        self.refresh_history()
        self.status_var.set(f"ลบ {len(sel_ids)} รายการแล้ว")

    def clear_all(self):
        if not self.appointments:
            return
        if messagebox.askyesno("ยืนยัน", "ต้องการล้างทั้งหมด? (ข้อมูลจะหายถาวรเมื่อปิดโปรแกรมอยู่แล้ว)"):
            self.appointments.clear()
            self.refresh_history()
            self.status_var.set("ล้างทั้งหมดแล้ว")

    # ================== Smart command handling ==================
    def handle_command(self, text: str) -> bool:
        """Detect and execute edit/delete commands. Return True if handled."""
        lowered = text.strip().lower()
        # Normalize Thai spaces
        if lowered.startswith('แก้นัด'):
            self.handle_edit_command(text)
            return True
        if lowered.startswith('ลบนัด'):
            self.handle_delete_command(text)
            return True
        return False

    def parse_index_or_title(self, phrase: str):
        """Try to interpret phrase as order number (แรก/ที่2/ที่3) or title substring."""
        phrase = phrase.strip()
        if phrase in ('แรก','อันแรก','รายการแรก'): return 1
        m = re.match(r'ที่(\d+)', phrase)
        if m:
            return int(m.group(1))
        # fallback: treat as title substring
        return phrase

    def find_appointment(self, selector):
        if isinstance(selector, int):
            if 1 <= selector <= len(self.appointments):
                return self.appointments[selector-1]
            return None
        # substring match by title
        for appt in self.appointments:
            if selector and selector in appt.get('appointment_title',''):
                return appt
        return None

    def handle_edit_command(self, text: str):
        """Support patterns:
        แก้นัด แรก นัดหมายเปลี่ยนจากAเป็นB
        แก้นัด นัดหมายXให้เปลี่ยนเป็นY
        """
        # Extract part after 'แก้นัด'
        after = text.split('แก้นัด',1)[1].strip()
        # Pattern 1: specify order word then 'นัดหมายเปลี่ยนจากAเป็นB'
        # Pattern 2: 'นัดหมาย<OLD>ให้เปลี่ยนเป็น<NEW>'
        # Simplify parsing with regex groups
        # Try pattern 1
        m1 = re.search(r'(แรก|อันแรก|รายการแรก|ที่\d+)\s*นัดหมายเปลี่ยนจาก(.+?)เป็น(.+)', after)
        if m1:
            selector_raw, old_txt, new_txt = m1.groups()
            selector = self.parse_index_or_title(selector_raw)
            appt = self.find_appointment(selector)
            if appt:
                appt['appointment_title'] = new_txt.strip()
                self.refresh_history()
                self.status_var.set("แก้นัดสำเร็จ")
            else:
                self.status_var.set("หาออเดอร์ไม่เจอ")
            return
        # Pattern 2
        m2 = re.search(r'นัดหมาย([^\s]+.*?)ให้เปลี่ยนเป็น(.+)', after)
        if m2:
            old_txt, new_txt = m2.groups()
            appt = self.find_appointment(old_txt.strip())
            if appt:
                appt['appointment_title'] = new_txt.strip()
                self.refresh_history()
                self.status_var.set("แก้นัดสำเร็จ")
            else:
                self.status_var.set("ไม่พบนัดที่ต้องการแก้")
            return
        self.status_var.set("รูปแบบคำสั่งแก้นัดไม่รองรับ ยังไม่แก้")

    def handle_delete_command(self, text: str):
        after = text.split('ลบนัด',1)[1].strip()
        # Try order
        m = re.match(r'(แรก|อันแรก|รายการแรก|ที่\d+)', after)
        if m:
            selector = self.parse_index_or_title(m.group(1))
            appt = self.find_appointment(selector)
            if appt:
                self.appointments = [a for a in self.appointments if a['id'] != appt['id']]
                self.refresh_history()
                self.status_var.set("ลบสำเร็จ")
            else:
                self.status_var.set("ไม่พบนัดที่จะลบ")
            return
        # By title fragment
        # Remove leading word 'นัดหมาย' if present
        after = after.replace('นัดหมาย','').strip()
        target = self.find_appointment(after)
        if target:
            self.appointments = [a for a in self.appointments if a['id'] != target['id']]
            self.refresh_history()
            self.status_var.set("ลบสำเร็จ")
        else:
            self.status_var.set("ไม่พบนัดที่จะลบ")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = SimpleParserTester(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()